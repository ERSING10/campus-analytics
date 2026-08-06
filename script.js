const KOCAELI_ADI = "Kocaeli Üniversitesi";
const RENK_KOCAELI = "#16a34a";
const RENK_DIGER = ["#1e3a5f", "#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#0ea5e9", "#0891b2", "#06b6d4", "#22d3ee"];

const UNI_RENKLERI = {
  "Boğaziçi Üniversitesi": "#0f2a52",
  "Koç Üniversitesi": "#a6192e",
  "Bilkent Üniversitesi": "#00205b",
  "Hacettepe Üniversitesi": "#f7b500",
  "Ankara Üniversitesi": "#c8102e",
  "İstanbul Teknik Üniversitesi": "#00325a",
  "Istanbul Üniversitesi": "#c8102e",
  "Orta Doğu Teknik Üniversitesi (ODTÜ)": "#00543c",
  "Gazi Üniversitesi": "#c8102e",
  "Sağlık Bilimleri Üniversitesi": "#d21f3c",
  "Ege Üniversitesi": "#003865",
  "Atatürk Üniversitesi": "#00274d",
  "Dokuz Eylül Üniversitesi": "#002d56",
  "Marmara Üniversitesi": "#00337a",
  "Yıldız Teknik Üniversitesi": "#d21f3c",
  "Selçuk Üniversitesi": "#1a7a3c",
  "Erciyes Üniversitesi": "#c8102e",
  "Çukurova Üniversitesi": "#1a7a3c",
  "Ondokuz Mayıs Üniversitesi": "#c8102e",
  "Karadeniz Teknik Üniversitesi": "#0a6e6e",
  "Bursa Uludağ Üniversitesi": "#1a7a3c",
  "Akdeniz Üniversitesi": "#0e8a9c",
  "Fırat Üniversitesi": "#1f4e8c",
  "İstanbul Üniversitesi-Cerrahpaşa": "#8c1c2e",
};

function uniRengi(universityName, yedekIndex) {
  if (universityName === KOCAELI_ADI) return RENK_KOCAELI;
  if (UNI_RENKLERI[universityName]) return UNI_RENKLERI[universityName];
  return RENK_DIGER[yedekIndex % RENK_DIGER.length];
}
let pastaChart = null;
let raporVerisi = null;    // report.json (10G/30G/momentum burdan gelir, seçilen tarihten etkilenmez)
let gunlukVeri = {};        // { "2026-07-29": { "Kocaeli Üniversitesi": 1234, ... }, ... }
let tarihListesi = [];

function tabloyuCiz(secilenTarih) {
  const gununDegerleri = gunlukVeri[secilenTarih] || {};

  const unis = raporVerisi.universities.map(u => ({
    ...u,
    gosterilen_deger: gununDegerleri[u.university] !== undefined ? gununDegerleri[u.university] : null,
  }));

  const gecerliUnis = unis.filter(u => u.gosterilen_deger !== null);
  const siraliListe = [...gecerliUnis].sort((a, b) => b.gosterilen_deger - a.gosterilen_deger);
  const kocaeli = unis.find(u => u.university === KOCAELI_ADI);
  const kocaeliSira = siraliListe.findIndex(u => u.university === KOCAELI_ADI) + 1;
  const enYuksek = siraliListe[0];

  document.getElementById("alt-baslik").innerText =
    unis.length + " üniversite izleniyor · Gösterilen tarih: " + secilenTarih;

  document.getElementById("kart-satiri").innerHTML = `
    <div class="kart">
      <div class="kart-baslik">Toplam Üniversite</div>
      <div class="kart-deger">${unis.length}</div>
    </div>
    <div class="kart vurgu">
      <div class="kart-baslik">Kocaeli Üniversitesi - Toplam Yayın</div>
      <div class="kart-deger">${kocaeli && kocaeli.gosterilen_deger !== null ? kocaeli.gosterilen_deger.toLocaleString("tr-TR") : "-"}</div>
      <div class="kart-alt">${kocaeliSira > 0 ? unis.length + " üniversite arasında " + kocaeliSira + ". sırada" : "bu tarihte veri yok"}</div>
    </div>
  `;

  const topListe = document.getElementById("top-liste");
  topListe.innerHTML = "";
  raporVerisi.top_gainers.forEach(g => {
    const li = document.createElement("li");
    if (g.university === KOCAELI_ADI) li.className = "kocaeli-satir";
    const rozetMetin = g.change_pct !== null ? "%" + g.change_pct : "—";
    li.innerHTML = `<span>${g.university}</span><span class="rozet">${rozetMetin}</span>`;
    topListe.appendChild(li);
  });

  // Pasta grafiği: Kocaeli + Kocaeli'den yüksek olan üniversiteler (farkı görmek için)
  let pastaVerisi;
  if (kocaeli && kocaeli.gosterilen_deger !== null) {
    const ustteki = gecerliUnis
      .filter(u => u.university !== KOCAELI_ADI && u.gosterilen_deger > kocaeli.gosterilen_deger)
      .sort((a, b) => b.gosterilen_deger - a.gosterilen_deger);
    pastaVerisi = [...ustteki, kocaeli];
  } else {
    pastaVerisi = siraliListe.slice(0, 10);
  }

  const renkler = pastaVerisi.map((u, i) => uniRengi(u.university, i));
  if (pastaChart) pastaChart.destroy();
  pastaChart = new Chart(document.getElementById("pastaGrafik"), {
    type: "doughnut",
    data: { labels: pastaVerisi.map(u => u.university), datasets: [{ data: pastaVerisi.map(u => u.gosterilen_deger), backgroundColor: renkler }] },
    options: { plugins: { legend: { position: "right", labels: { boxWidth: 12, font: { size: 11 } } } } }
  });

  const govde = document.getElementById("tablo-govdesi");
  govde.innerHTML = "";
  const tabloSirali = [...unis].sort((a, b) => {
    if (a.gosterilen_deger === null) return 1;
    if (b.gosterilen_deger === null) return -1;
    return b.gosterilen_deger - a.gosterilen_deger;
  });
  tabloSirali.forEach(uni => {
    const c10 = uni.change_10d.change_pct !== null ? uni.change_10d.change_pct + "%" : '<span class="yetersiz">yetersiz veri</span>';
    const c30 = uni.change_30d.change_pct !== null ? uni.change_30d.change_pct + "%" : '<span class="yetersiz">yetersiz veri</span>';
    const mom = uni.momentum.momentum !== null ? uni.momentum.momentum : '<span class="yetersiz">yetersiz veri</span>';
    const sayi = uni.gosterilen_deger !== null ? uni.gosterilen_deger.toLocaleString("tr-TR") : '<span class="yetersiz">bu tarihte veri yok</span>';

    const satir = document.createElement("tr");
    if (uni.university === KOCAELI_ADI) satir.className = "kocaeli-satir";
    satir.innerHTML = `
      <td>${uni.university}</td>
      <td class="sayi">${sayi}</td>
      <td class="sayi">${c10}</td>
      <td class="sayi">${c30}</td>
      <td class="sayi">${mom}</td>
    `;
    govde.appendChild(satir);
  });
}

Promise.all([
  fetch("report.json?t=" + Date.now()).then(r => r.json()),
  fetch("data/gunluk_ozet.csv?t=" + Date.now()).then(r => r.text()),
]).then(([rapor, csvText]) => {
  raporVerisi = rapor;

  const gunlukToplam = {};
  csvText.trim().split("\n").slice(1).forEach(satir => {
    if (!satir) return;
    const [tarih, uni, deger] = satir.split(",");
    if (!gunlukVeri[tarih]) gunlukVeri[tarih] = {};
    gunlukVeri[tarih][uni] = parseFloat(deger);

    if (!gunlukToplam[tarih]) gunlukToplam[tarih] = 0;
    gunlukToplam[tarih] += parseFloat(deger);
  });

  tarihListesi = Object.keys(gunlukVeri).sort();

  const secici = document.getElementById("tarih-secici");

  if (tarihListesi.length === 0) {
    document.getElementById("alt-baslik").innerText = "Henüz veri yok — ilk otomatik çalışmadan sonra burada görünecek.";
    document.querySelector(".tarih-secici-satiri").style.display = "none";
    return;
  }

  // en yeni tarih listede en üstte görünsün
  [...tarihListesi].reverse().forEach(tarih => {
    const opt = document.createElement("option");
    opt.value = tarih;
    opt.textContent = tarih;
    secici.appendChild(opt);
  });

  const enGuncelTarih = tarihListesi[tarihListesi.length - 1];
  secici.value = enGuncelTarih;
  secici.addEventListener("change", () => tabloyuCiz(secici.value));

  tabloyuCiz(enGuncelTarih);

  const son30Gun = tarihListesi.slice(-30);
  new Chart(document.getElementById("aktiviteGrafik"), {
    type: "line",
    data: {
      labels: son30Gun,
      datasets: [{ label: "Toplam İzlenen Yayın Sayısı", data: son30Gun.map(t => gunlukToplam[t]), borderColor: "#1e3a5f", backgroundColor: "rgba(30,58,95,0.08)", fill: true, tension: 0.2, pointRadius: 4 }]
    },
    options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: false } } }
  });
});
