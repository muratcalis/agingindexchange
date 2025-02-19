import pandas as pd
import matplotlib.pyplot as plt


def process_gene_changes(file_path, tissue_name, excel_output_path, show_nonzero_only=False):
    # Dosyayı oku
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Dosya okunamadı: {file_path}, Hata: {e}")
        return

    # Değişim sütunlarını seç ve tüm satırlarda F_Value hesapla
    change_columns = [col for col in df.columns if col.startswith('Change_')]
    df['F_Value'] = df[change_columns].sum(axis=1) / 15

    # Tüm dokuların sonuçları için kopya oluştur
    df_all = df.copy()

    # Sadece ilgili dokuya ait verileri filtrele
    df = df[df['Tissue'] == tissue_name]

    # Sıfır olmayan değerler filtrele (isteğe bağlı)
    #if show_nonzero_only:
    #    df = df[df['F_Value'] != 0]

    # Genleri F_Value değerine göre büyükten küçüğe sırala
    df = df.sort_values(by='F_Value', ascending=False)

    # Sonuçları yatay sütunlar (genler) ve dikey değerler olarak yeniden düzenle
    result_df = df[['Gene', 'F_Value']].set_index('Gene').T

    # Excel dosyasına tüm dokuların sonuçlarını ve ilgili doku sonuçlarını ayrı sayfalarda kaydet
    try:
        with pd.ExcelWriter(excel_output_path) as writer:
            df_all.to_excel(writer, sheet_name="All_Tissues", index=False)
            df.to_excel(writer, sheet_name=tissue_name, index=False)
        print(f"Sıralanmış veriler '{excel_output_path}' dosyasına kaydedildi.")
    except Exception as e:
        print(f"Excel dosyasına kaydedilemedi: {e}")

    # Grafiği çiz (Çizgi Grafik) - x ekseninde gen isimleri gösterilmiyor
    plt.figure(figsize=(10, 5))
    x_values = list(range(len(result_df.columns)))
    plt.plot(x_values, result_df.loc['F_Value'], marker='o', linestyle='-', color='b', label="F(g_k, T)")

    plt.xlabel("Genler")
    plt.ylabel("F(g_k, T) Values")
    plt.title(f"F(g_k, T) Values for {tissue_name}")
    plt.xticks(x_values, [])
    plt.grid(axis='both', linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.show()

    return result_df


# Kullanım
if __name__ == "__main__":
    file_path = "./output/gene_degree_changes_m_1.csv"  # Gen değişim dosyası
    tissue_name = "mapped_brain_cortex"  # Doku adı, belirtilen doku adını excelde tek sayfaya yazar. ayrıca tüm dokular olarak ta ALL_tissues sekmesinde yazar
    excel_output_path ="./output/" + tissue_name + "_sorted_gene_changes_m_1.xlsx"  # Sıralanmış genlerin kaydedildiği dosya değişim dosyası

    result = process_gene_changes(file_path, tissue_name, excel_output_path, show_nonzero_only=True)
    if result is not None:
        print("Sonuçlar:")
        print(result)

