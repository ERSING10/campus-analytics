const KOCAELI_ADI = "Kocaeli Üniversitesi";
const RENK_KOCAELI = "#16a34a";
const RENK_DIGER = ["#1e3a5f", "#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#0ea5e9", "#0891b2", "#06b6d4", "#22d3ee"];

fetch("report.json?t=" + Date.now())
  .then(response => response.json())
  .then(rapor => {
    const unis = rapor.universities;
    const kocaeli = unis.find(u => u.university === KOCAELI_ADI);
    const siraliListe = [...unis].sort((a, b) => b.new_value - a.new_value);
    const kocaeliSira = siraliListe.findIndex(u => u.university === KOCAELI_ADI) + 1;
    const enYuksek = siraliListe[0];

    document.getElementById("alt-baslik").innerText =
      unis.length + " üniversite izleniyor · Son güncelleme: " + new Date().toLocaleString("tr-TR");

    document.getElementById("kart-satiri").innerHTML = `
      <div class="kart">
        <div class="kart-baslik">Toplam Üniversite</div>
        <div class="kart-deger">${unis.length}</div>
      </div>
      <div class="kart vurgu">
        <div class="kart-baslik">Kocaeli Üniversitesi - Toplam Yayın</div>
        <div class="kart-deger">${kocaeli ? kocaeli.new_value.toLocaleString("tr-TR") : "-"}</div>
        <div class="kart-alt">${unis.length} üniversite arasında ${kocaeliSira}. sırada</div>
      </div>
      <div class="kart">
        <div class="kart-baslik">En Yüksek Yayın Sayısı</div>
        <div class="kart-deger">${enYuksek.new_value.toLocaleString("tr-TR")}</div>
        <div class="kart-alt">${enYuksek.university}</div>
      </div>
    `;

    const topListe = document.getElementById("top-liste");
    rapor.top_gainers.forEach(g => {
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
    new Chart(document.getElementById("pastaGrafik"), {
      type: "doughnut",
      data: { labels: ilk10.map(u => u.university), datasets: [{ data: ilk10.map(u => u.new_value), backgroundColor: renkler }] },
      options: { plugins: { legend: { position: "right", labels: { boxWidth: 12, font: { size: 11 } } } } }
    });

    const govde = document.getElementById("tablo-govdesi");
    unis.forEach(uni => {
      const c10 = uni.change_10d.change_pct !== null ? uni.change_10d.change_pct + "%" : '<span class="yetersiz">yetersiz veri</span>';
      const c30 = uni.change_30d.change_pct !== null ? uni.change_30d.change_pct + "%" : '<span class="yetersiz">yetersiz veri</span>';
      const mom = uni.momentum.momentum !== null ? uni.momentum.momentum : '<span class="yetersiz">yetersiz veri</span>';
      const est = uni.year_end_estimate.estimate !== null ? uni.year_end_estimate.estimate.toLocaleString("tr-TR") : '<span class="yetersiz">yetersiz veri</span>';

      const satir = document.createElement("tr");
      if (uni.university === KOCAELI_ADI) satir.className = "kocaeli-satir";
      satir.innerHTML = `
        <td>${uni.university}</td>
        <td class="sayi">${uni.new_value.toLocaleString("tr-TR")}</td>
        <td class="sayi">${c10}</td>
        <td class="sayi">${c30}</td>
        <td class="sayi">${mom}</td>
        <td class="sayi">${est}</td>
      `;
      govde.appendChild(satir);
    });
  });

fetch("data/gunluk_ozet.csv?t=" + Date.now())
  .then(response => response.text())
  .then(csvText => {
    const satirlar = csvText.trim().split("\n").slice(1);
    const gunlukToplam = {};
    satirlar.forEach(satir => {
      const [tarih, uni, deger] = satir.split(",");
      if (!gunlukToplam[tarih]) gunlukToplam[tarih] = 0;
      gunlukToplam[tarih] += parseFloat(deger);
    });
    const tarihler = Object.keys(gunlukToplam).sort();
    new Chart(document.getElementById("aktiviteGrafik"), {
      type: "line",
      data: {
        labels: tarihler,
        datasets: [{ label: "Toplam İzlenen Yayın Sayısı", data: tarihler.map(t => gunlukToplam[t]), borderColor: "#1e3a5f", backgroundColor: "rgba(30,58,95,0.08)", fill: true, tension: 0.2, pointRadius: 4 }]
      },
      options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: false } } }
    });
  });