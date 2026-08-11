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
let raporVerisi = null;
let gunlukVeri = {};
let tarihListesi = [];


function kartlariDoldur(unis, odakUni, odakSira) {
  const kartAlani = document.getElementById("kart-satiri");

  const odakDegeri = odakUni && odakUni.gosterilen_deger !== null
    ? odakUni.gosterilen_deger.toLocaleString("tr-TR")
    : "-";

  const odakAltYazi = odakSira > 0
    ? unis.length + " üniversite arasında " + odakSira + ". sırada"
    : "bu tarihte veri yok";

  kartAlani.innerHTML = `
    <div class="kart">
      <div class="kart-baslik">Toplam Üniversite</div>
      <div class="kart-deger">${unis.length}</div>
    </div>
    <div class="kart vurgu">
      <div class="kart-baslik">Kocaeli Üniversitesi - Toplam Yayın</div>
      <div class="kart-deger">${odakDegeri}</div>
      <div class="kart-alt">${odakAltYazi}</div>
    </div>
  `;
}


function enCokArtanlariDoldur(topGainers) {
  const listeAlani = document.getElementById("top-liste");
  listeAlani.innerHTML = "";

  topGainers.forEach(uni => {
    const satir = document.createElement("li");

    if (uni.university === KOCAELI_ADI) {
      satir.className = "kocaeli-satir";
    }

    const yuzdeMetni = uni.change_pct !== null ? "%" + uni.change_pct : "—";
    satir.innerHTML = `<span>${uni.university}</span><span class="rozet">${yuzdeMetni}</span>`;

    listeAlani.appendChild(satir);
  });
}


function daha_buyuk_universiteler(unis, odakUni) {
  const sonuc = [];

  for (const uni of unis) {
    const farkliUni = uni.university !== odakUni.university;
    const buyukDeger = uni.gosterilen_deger > odakUni.gosterilen_deger;

    if (farkliUni && buyukDeger) {
      sonuc.push(uni);
    }
  }

  sonuc.sort((a, b) => b.gosterilen_deger - a.gosterilen_deger);
  return sonuc;
}

function pastaGrafiginiCiz(gecerliUnis, siraliListe, odakUni) {
  let pastaVerisi;

  if (odakUni && odakUni.gosterilen_deger !== null) {
    const ustteki = daha_buyuk_universiteler(gecerliUnis, odakUni);
    pastaVerisi = [...ustteki, odakUni];
  } else {
    pastaVerisi = siraliListe.slice(0, 10);
  }

  const renkler = [];
  for (let i = 0; i < pastaVerisi.length; i++) {
    renkler.push(uniRengi(pastaVerisi[i].university, i));
  }

  if (pastaChart) {
    pastaChart.destroy();
  }

  pastaChart = new Chart(document.getElementById("pastaGrafik"), {
    type: "doughnut",
    data: {
      labels: pastaVerisi.map(uni => uni.university),
      datasets: [{ data: pastaVerisi.map(uni => uni.gosterilen_deger), backgroundColor: renkler }]
    },
    options: {
      plugins: { legend: { position: "right", labels: { boxWidth: 12, font: { size: 11 } } } }
    }
  });
}


function tabloyuDoldur(unis) {
  const govde = document.getElementById("tablo-govdesi");
  govde.innerHTML = "";

  const siraliTablo = [...unis].sort((a, b) => {
    if (a.gosterilen_deger === null) return 1;
    if (b.gosterilen_deger === null) return -1;
    return b.gosterilen_deger - a.gosterilen_deger;
  });

  for (const uni of siraliTablo) {
    const c10 = uni.change_10d.change_pct !== null
      ? uni.change_10d.change_pct + "%"
      : '<span class="yetersiz">yetersiz veri</span>';

    const c30 = uni.change_30d.change_pct !== null
      ? uni.change_30d.change_pct + "%"
      : '<span class="yetersiz">yetersiz veri</span>';

    const mom = uni.momentum.momentum !== null
      ? uni.momentum.momentum
      : '<span class="yetersiz">yetersiz veri</span>';

    const sayi = uni.gosterilen_deger !== null
      ? uni.gosterilen_deger.toLocaleString("tr-TR")
      : '<span class="yetersiz">bu tarihte veri yok</span>';

    const satir = document.createElement("tr");

    if (uni.university === KOCAELI_ADI) {
      satir.className = "kocaeli-satir";
    }

    satir.innerHTML = `
      <td>${uni.university}</td>
      <td class="sayi">${sayi}</td>
      <td class="sayi">${c10}</td>
      <td class="sayi">${c30}</td>
      <td class="sayi">${mom}</td>
    `;

    govde.appendChild(satir);
  }
}

function rakipleriDoldur(rakipler) {
  if (!rakipler || !rakipler.kocaeli) return;

  const rakipListe = document.getElementById("rakip-liste");
  rakipListe.innerHTML = "";

  for (const uni of rakipler.above) {
    const satir = document.createElement("li");
    satir.innerHTML = `<span>${uni.university}</span><span class="rozet-notr">${uni.new_value.toLocaleString("tr-TR")}</span>`;
    rakipListe.appendChild(satir);
  }

  const kocaeliSatir = document.createElement("li");
  kocaeliSatir.className = "kocaeli-satir";
  kocaeliSatir.innerHTML = `<span>Kocaeli Üniversitesi (${rakipler.sira}. sıra)</span><span class="rozet">${rakipler.kocaeli.new_value.toLocaleString("tr-TR")}</span>`;
  rakipListe.appendChild(kocaeliSatir);

  for (const uni of rakipler.below) {
    const satir = document.createElement("li");
    satir.innerHTML = `<span>${uni.university}</span><span class="rozet-notr">${uni.new_value.toLocaleString("tr-TR")}</span>`;
    rakipListe.appendChild(satir);
  }
}


function tabloyuCiz(secilenTarih) {
  const gununDegerleri = gunlukVeri[secilenTarih] || {};

  const unis = raporVerisi.universities.map(uni => ({
    ...uni,
    gosterilen_deger: gununDegerleri[uni.university] !== undefined ? gununDegerleri[uni.university] : null,
  }));

  const gecerliUnis = unis.filter(uni => uni.gosterilen_deger !== null);
  const siraliListe = [...gecerliUnis].sort((a, b) => b.gosterilen_deger - a.gosterilen_deger);

  const odakUni = unis.find(uni => uni.university === KOCAELI_ADI);
  const odakSira = siraliListe.findIndex(uni => uni.university === KOCAELI_ADI) + 1;

  document.getElementById("alt-baslik").innerText =
    unis.length + " üniversite izleniyor · Gösterilen tarih: " + secilenTarih;

  kartlariDoldur(unis, odakUni, odakSira);
  enCokArtanlariDoldur(raporVerisi.top_gainers);
  pastaGrafiginiCiz(gecerliUnis, siraliListe, odakUni);
  tabloyuDoldur(unis);
  rakipleriDoldur(raporVerisi.closest_rivals);
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