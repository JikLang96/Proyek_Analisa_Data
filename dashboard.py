import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="Dashboard Bike Sharing",
    page_icon="https://raw.githubusercontent.com/JikLang96/Logo_sepeda/refs/heads/main/favicon.ico"
)
sns.set(style='dark')

def hitung_total_per_jam(jam_df):
  hitung_jam_df =  jam_df.groupby(by="hr").agg({"cnt": ["sum"]})
  return hitung_jam_df

def hitung_total_per_hari(hari_df):
    hitung_data_hari = hari_df.query(str('dteday >= "2011-01-01" and dteday < "2012-12-31"'))
    return hitung_data_hari

def total_registered_df(hari_df):
   regis_df =  hari_df.groupby(by="dteday").agg({
      "registered": "sum"
    })
   regis_df = regis_df.reset_index()
   regis_df.rename(columns={
        "registered": "register_sum"
    }, inplace=True)
   return regis_df

def total_casual_df(hari_df):
   casual_df =  hari_df.groupby(by="dteday").agg({
      "casual": ["sum"]
    })
   casual_df = casual_df.reset_index()
   casual_df.rename(columns={
        "casual": "casual_sum"
    }, inplace=True)
   return casual_df

def hitung_order (jam_df):
    total_jumlah_order = jam_df.groupby("hr").cnt.sum().sort_values(ascending=False).reset_index()
    return total_jumlah_order

def jenis_musim (jam_df): 
    musim_df = jam_df.groupby(by="season").cnt.sum().reset_index() 
    return musim_df

data_hari="https://raw.githubusercontent.com/JikLang96/Proyek_Analisa_Data/refs/heads/main/data_hari.csv"
data_jam="https://raw.githubusercontent.com/JikLang96/Proyek_Analisa_Data/refs/heads/main/data_jam.csv"
hari_df = pd.read_csv(data_hari)
jam_df = pd.read_csv(data_jam)

kolom_date = ["dteday"]
hari_df.sort_values(by="dteday", inplace=True)
jam_df.reset_index(inplace=True)   

hari_df.sort_values(by="dteday", inplace=True)
jam_df.reset_index(inplace=True)

for column in kolom_date:
    hari_df[column] = pd.to_datetime(hari_df[column])
    jam_df[column] = pd.to_datetime(jam_df[column])

min_hari = hari_df["dteday"].min()
max_hari = hari_df["dteday"].max()

min_jam = jam_df["dteday"].min()
max_jam = jam_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://raw.githubusercontent.com/JikLang96/Logo_sepeda/refs/heads/main/logo%20sepeda.webp")
    
    # Membuat rentang waktu dengan date_input
    date_selection = st.date_input(
    label='Rentang Waktu',
    min_value=min_hari,
    max_value=max_hari,
    value=[min_hari, max_hari]
)
    
# Mengatur start date agar ketika memilih satu rentang tanggal tidak terjadi error
if isinstance(date_selection, tuple) or isinstance(date_selection, list):
    if len(date_selection) == 2:
        start_date, end_date = date_selection
    else:
        start_date = date_selection[0]
        end_date = date_selection[0]
else:
    start_date = date_selection
    end_date = date_selection
  
main_hari = hari_df[(hari_df["dteday"] >= str(start_date)) & 
                       (hari_df["dteday"] <= str(end_date))]

main_jam = jam_df[(jam_df["dteday"] >= str(start_date)) & 
                        (jam_df["dteday"] <= str(end_date))]

hour_count_df = hitung_total_per_jam(main_jam)
day_df_count_2011 = hitung_total_per_hari(main_hari)
regis_df = total_registered_df(main_hari)
casual_df = total_casual_df(main_hari)
sum_order_items_df = hitung_order(main_jam)
season_df = jenis_musim(main_jam)

#Melengkapi Dashboard dengan Berbagai Visualisasi Data
# Header utama
st.header('🚴 Bike Sharing ')

# Subheader untuk data harian
st.subheader('📊 Data Harian')

# Membagi layout menjadi tiga kolom
col1, col2, col3 = st.columns(3)

with col1:
    total_orders = day_df_count_2011.cnt.sum()
    st.metric("🚲 Total Sewa Sepeda", value=f"{total_orders:,}")

with col2:
    total_sum_regis = regis_df.register_sum.sum()
    st.metric("👤 Total Registered", value=f"{total_sum_regis:,}")

with col3:
    total_sum_casual = casual_df.casual_sum.sum()  

if isinstance(total_sum_casual, (int, float)):
        total_sum_casual_formatted = f"{total_sum_casual:,}"
else:
        total_sum_casual_formatted = f"{total_sum_casual.item():,}"  # Ambil nilai tunggal jika masih Series

st.metric("🛑 Total Casual", value=total_sum_casual_formatted)

st.subheader("Performa penjualan dalam beberapa tahun") #subheader

fig1=plt.figure(figsize=(20, 4))

# Mengonversi kolom 'dteday' ke format datetime jika belum
#hari_df["dteday"] = pd.to_datetime(hari_df["dteday"])

# Menghitung jumlah pelanggan maksimum per bulan
trend_bulanan = main_hari.groupby(main_hari["dteday"].dt.to_period("M"))["cnt"].sum()

# Membuat scatter plot serta mengatur sumbu, judul, dan grid
plt.scatter(trend_bulanan.index.astype(str), trend_bulanan.values, c="cyan", s=10, marker='o', label="Total pelanggan")
plt.plot(trend_bulanan.index.astype(str), trend_bulanan.values, linestyle="-", color="blue", alpha=0.7)

# Menambahkan data label di setiap titik
for i, txt in enumerate(trend_bulanan.values):
    plt.text(trend_bulanan.index.astype(str)[i], txt + 5, f"{txt:.0f}", ha="center", fontsize=10, color="black")


plt.grid(True, linestyle="--", alpha=0.7)
plt.ylabel("Jumlah Pelanggan", fontsize=12)
plt.title("Trend Penjualan Perusahaan", fontsize=14)
plt.xticks(rotation=45, fontsize=10)
plt.legend()
st.pyplot(fig1)

st.subheader("Total Pelanggan tiap musimnya") #subheader

pivot = main_hari.groupby('season')['cnt'].sum()
# Membuat barplot berdasarkan pivot_data yang telah dihitung
fig, ax = plt.subplots(figsize=(15, 8))
sns.barplot(
    x=pivot.index,
    y=pivot.values,
    ax=ax
)

# Menambahkan data label pada tiap barplot
for p in ax.patches:
    ax.text(
        p.get_x() + p.get_width() / 2,
        p.get_height() + 5,
        f'{p.get_height():.0f}',
        ha='center',
        va='bottom',
        fontsize=16,
        color='black'
    )

# Menambahkan judul dan label
ax.set_title("Jumlah Pelanggan Tiap Musimnya", loc="center", fontsize=30)
ax.set_xlabel(None)
ax.set_ylabel(None)
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=20)

# Menampilkan plot
st.pyplot(fig)


st.subheader("Perbandingan Pelanggan yang Registered dengan Casual")

fig1=plt.figure(figsize=(10, 6))

# membuat variable jumlah dan pengguna
pengguna = ['Registered', 'Casual']
jumlah = [main_hari['registered'].sum(), main_hari['casual'].sum()]

# Menentukan posisi sumbu-x
x_pos = [0, 1]  # Posisi untuk "Registered" dan "Casual"

# Membuat bar chart
bars=plt.bar(x_pos[0], jumlah[0], width=0.4, label='Register', align='center', color='blue')
bars2=plt.bar(x_pos[1], jumlah[1], width=0.4, label='Casual', align='center', color='blue')


# Menambahkan label data pada setiap batang
for bar in bars:
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5, 
             f'{bar.get_height():.0f}', ha='center', va='bottom', color='black', fontsize=12)

for bar in bars2:
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5, 
             f'{bar.get_height():.0f}', ha='center', va='bottom', color='black', fontsize=12)

# Menambahkan label dan judul
plt.xticks(x_pos, pengguna)  # Menambahkan label untuk x-axis
plt.grid(True, linestyle='--', alpha=0.7)  # Menambahkan grid dengan garis putus-putus
plt.xlabel('Kategori Pelanggan')
plt.ylabel('Jumlah Pelanggan')
plt.title('Perbandingan Pelanggan Register dan Casual', fontsize=14)
#plt.legend(title="Jenis Pelanggan")

# Menampilkan plot
st.pyplot(fig1)
