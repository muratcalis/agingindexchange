import os
import pandas as pd
from collections import defaultdict

# Klasörler ve dosyaları işlemek için ana fonksiyon
def process_folders(base_path):
    # Tüm networkteki genlerin birleşimi için bir set
    all_genes = set()

    # Her yaş grubu ve doku için hesaplanacak in-degree değerlerini tutan sözlük
    degree_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    # Her yaş grubu için klasörleri döngüyle işle
    for age_folder in ["20", "30", "40", "50", "60", "70"]:
        folder_path = os.path.join(base_path, age_folder)

        if not os.path.exists(folder_path):
            print(f"Klasör bulunamadı: {folder_path}")
            continue

        # Klasördeki CSV dosyalarını işle
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".csv"):
                file_path = os.path.join(folder_path, file_name)
                tissue_name = os.path.splitext(file_name)[0]  # Dosya adından doku adı çıkarma
                tissue_base_name = tissue_name.rsplit('_', 1)[0]  # Yaş ekini kaldırma

                # CSV dosyasını oku
                try:
                    df = pd.read_csv(file_path)
                except Exception as e:
                    print(f"Dosya okunamadı: {file_path}, Hata: {e}")
                    continue

                # Genler arası ilişkileri işleme (in-degree hesaplanıyor)
                for _, row in df.iterrows():
                    gene_a, gene_b = row['GeneA'], row['GeneB']

                    # Genleri tüm networke ekle
                    all_genes.update([gene_a, gene_b])

                    # In-degree hesaplama: Sadece hedef gen (gene_b) için dereceyi arttır
                    degree_dict[age_folder][tissue_base_name][gene_b] += 1

    return all_genes, degree_dict

# Hesaplanan düğüm (in-degree) değerlerini satırlarda yaş ve doku isimleri, sütunlarda gen isimleri olacak şekilde kaydetme fonksiyonu
def save_degree_matrix_to_files(all_genes, degree_dict, csv_output_file, excel_output_file):
    # Tüm genleri alfabetik sırayla al
    all_genes = sorted(all_genes)

    # DataFrame oluşturmak için liste
    data = []

    for age_folder, tissues in degree_dict.items():
        for tissue_name, genes in tissues.items():
            row = {"AgeGroup": age_folder, "Tissue": tissue_name}
            for gene in all_genes:
                row[gene] = genes.get(gene, 0)
            data.append(row)

    # DataFrame oluştur
    df = pd.DataFrame(data)

    # CSV olarak kaydet
    df.to_csv(csv_output_file, index=False)
    print(f"Gen in-degree matris olarak CSV formatında kaydedildi: {csv_output_file}")

    # Excel olarak kaydet
    df.to_excel(excel_output_file, index=False)
    print(f"Gen in-degree matris olarak Excel formatında kaydedildi: {excel_output_file}")

# In-degree değişimlerini hesaplayıp kaydetme fonksiyonu
def save_degree_changes_to_files(all_genes, degree_dict, csv_output_file, excel_output_file):
    all_genes = sorted(all_genes)
    age_groups = ["20", "30", "40", "50", "60", "70"]

    data = []

    for tissue_name in {t for ages in degree_dict.values() for t in ages}:
        for gene in all_genes:
            row = {"Tissue": tissue_name, "Gene": gene}
            for i in range(len(age_groups) - 1):
                current_age = age_groups[i]
                next_age = age_groups[i + 1]
                current_degree = degree_dict[current_age].get(tissue_name, {}).get(gene, 0)
                next_degree = degree_dict[next_age].get(tissue_name, {}).get(gene, 0)
                change = (1 if next_degree > current_degree else -1 if next_degree < current_degree else 0)
                row[f"Change_{current_age}_to_{next_age}"] = change
            data.append(row)

    # Son yaş değişimlerini kontrol et ve ekle
    for tissue_name in {t for ages in degree_dict.values() for t in ages}:
        for gene in all_genes:
            last_index = len(age_groups) - 1
            penultimate_age = age_groups[last_index - 1]
            last_age = age_groups[last_index]
            penultimate_degree = degree_dict[penultimate_age].get(tissue_name, {}).get(gene, 0)
            last_degree = degree_dict[last_age].get(tissue_name, {}).get(gene, 0)
            last_change = (1 if last_degree > penultimate_degree else -1 if last_degree < penultimate_degree else 0)
            for row in data:
                if row["Tissue"] == tissue_name and row["Gene"] == gene:
                    row[f"Change_{penultimate_age}_to_{last_age}"] = last_change

    # DataFrame oluştur
    df = pd.DataFrame(data)

    # CSV olarak kaydet
    df.to_csv(csv_output_file, index=False)
    print(f"In-degree değişimleri CSV formatında kaydedildi: {csv_output_file}")

    # Excel olarak kaydet
    df.to_excel(excel_output_file, index=False)
    print(f"In-degree değişimleri Excel formatında kaydedildi: {excel_output_file}")

# Ana işlem
if __name__ == "__main__":
    # Veri ve çıktı yollarını ayarla
    base_path = "./mapped"  # Klasörlerin bulunduğu ana dizin
    csv_output_file = "./output/gene_degree_matrix_m_1.csv"  # CSV çıktısı dosyasının yolu
    excel_output_file = "./output/gene_degree_matrix_m_1.xlsx"  # Excel çıktısı dosyasının yolu
    change_csv_output_file = "./output/gene_degree_changes_m_1.csv"  # Değişim CSV çıktısı dosyasının yolu
    change_excel_output_file = "./output/gene_degree_changes_m_1.xlsx"  # Değişim Excel çıktısı dosyasının yolu

    # Çıktı klasörünü oluştur
    os.makedirs(os.path.dirname(csv_output_file), exist_ok=True)

    # İşlemleri başlat
    all_genes, degree_dict = process_folders(base_path)

    # In-degree matrisini dosyalara kaydet
    save_degree_matrix_to_files(all_genes, degree_dict, csv_output_file, excel_output_file)

    # In-degree değişimlerini dosyalara kaydet
    save_degree_changes_to_files(all_genes, degree_dict, change_csv_output_file, change_excel_output_file)
