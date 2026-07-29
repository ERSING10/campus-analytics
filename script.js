const KOCAELI_ADI = "Kocaeli Üniversitesi";
const RENK_KOCAELI = "#16a34a";
const RENK_DIGER = ["#1e3a5f", "#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#0ea5e9", "#0891b2", "#06b6d4", "#22d3ee"];

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
    <div class="kart">
      <div class="kart-baslik">En Yüksek Yayın Sayısı</div>
      <div class="kart-deger">${enYuksek ? enYuksek.gosterilen_deger.toLocaleString("tr-TR") : "-"}</div>
      <div class="kart-alt">${enYuksek ? enYuksek.university : ""}</div>
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

  const ilk10 = siraliListe.slice(0, 10);
  let renkIndex = 0;
  const renkler = ilk10.map(u => {
    if (u.university === KOCAELI_ADI) return RENK_KOCAELI;
    return RENK_DIGER[(renkIndex++) % RENK_DIGER.length];
  });
  if (pastaChart) pastaChart.destroy();
  pastaChart = new Chart(document.getElementById("pastaGrafik"), {
    type: "doughnut",
    data: { labels: ilk10.map(u => u.university), datasets: [{ data: ilk10.map(u => u.gosterilen_deger), backgroundColor: renkler }] },
    options: { plugins: { legend: { position: "right", labels: { boxWidth: 12, font: { size: 11 } } } } }
  });

  const govde = document.getElementById("tablo-govdesi");
  govde.innerHTML = "";
  unis.forEach(uni => {
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
