const principles = [
  {
    id: "01",
    heading: "正しい情報から組み立てる",
    body: "店舗固有の情報や料金を推測せず、確認済みの根拠だけを掲載します。",
  },
  {
    id: "02",
    heading: "お店らしさを伝える",
    body: "要件とデザイン定義を起点に、写真・言葉・余白の強弱を設計します。",
  },
  {
    id: "03",
    heading: "スマホで心地よく読める",
    body: "最も使われる画面を優先し、見出しと導線を丁寧に整えます。",
  },
];

export default function Home() {
  return (
    <>
      <a className="skip-link" href="#content">本文へスキップ</a>
      <header className="site-header">
        <div className="shell nav">
          <a className="brand" href="#top" aria-label="LPデモの先頭へ">
            <span className="brand-mark" aria-hidden="true">M</span>
            <span>MISEMIRU <small>LP LAB</small></span>
          </a>
          <a className="nav-link" href="#principles">制作方針を見る <span aria-hidden="true">↗</span></a>
        </div>
      </header>

      <main id="content">
        <section className="hero" id="top" aria-labelledby="hero-title">
          <div className="shell hero-grid">
            <div className="hero-copy">
              <p className="eyebrow">SAMPLE LP / DESIGN SYSTEM TEST</p>
              <h1 id="hero-title"><span className="hero-heading-line">「伝わる」を、</span><em className="hero-heading-line">設計する。</em></h1>
              <p className="hero-lead">店舗の魅力を、正確な情報と美しい体験で届ける。その第一歩を検証するためのデモページです。</p>
              <a className="button" href="#principles">制作方針を見る <span aria-hidden="true">↗</span></a>
              <p className="hero-note">※ 架空の制作環境確認用ページです。実在店舗の広告・予約ページではありません。</p>
            </div>
            <div className="hero-art" aria-hidden="true">
              <div className="hero-art-frame">
                <div className="art-circle" />
                <span className="art-index">01 / FIRST IMPRESSION</span>
                <span className="art-type">FORM<br />&amp; FEELING</span>
              </div>
            </div>
          </div>
        </section>

        <section className="intro-section" aria-label="このページについて">
          <div className="shell intro-inner">
            <span className="intro-number">EST. TEST</span>
            <p>これは、GitHub Pagesで安全に公開できるかを検証するための<strong>共通基盤</strong>です。実際の店舗LPは、個別の要件定義とデザイン審査を経て制作します。</p>
          </div>
        </section>

        <section id="principles" className="principles-section" aria-labelledby="principles-title">
          <div className="shell">
            <div className="section-heading">
              <p className="eyebrow">OUR APPROACH</p>
              <h2 id="principles-title">まず、守るべきこと。</h2>
              <p>魅力を演出する前に、安心して使えるページとしての土台を整えます。</p>
            </div>
            <div className="principles-grid">
              {principles.map((item) => (
                <article className="principle" key={item.id}>
                  <span className="principle-number">{item.id}</span>
                  <h3>{item.heading}</h3>
                  <p>{item.body}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="statement-section" aria-labelledby="statement-title">
          <div className="shell statement-inner">
            <p className="eyebrow">READY FOR REVIEW</p>
            <h2 id="statement-title">次は、あなたのお店だけの一枚へ。</h2>
            <p>このページには実在店舗の情報を含めていません。制作許可、画像権利、最新情報を確認してから、個別案件へ展開します。</p>
            <a className="text-link" href="#top">ページの先頭へ戻る <span aria-hidden="true">↑</span></a>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="shell footer-inner">
          <span>MISEMIRU LP LAB</span>
          <span>Internal workflow demonstration · no real customer data</span>
        </div>
      </footer>
    </>
  );
}
