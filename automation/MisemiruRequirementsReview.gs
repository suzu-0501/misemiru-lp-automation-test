/**
 * STEP 16: 要件定義レビュー台帳への安全な同期（検証専用）
 * Google Sheetsに紐づくApps Scriptとして追加する。AI APIへの送信はしない。
 */
function misemiruSyncRequirementsReviews_v1() {
  const expectedName = "ミセミルWeb_業務自動化_検証用_v1";
  const inputHeaders = ["店舗ID","店舗名","状態","不足情報・質問","要件定義用プロンプト","人間の承認","生成日時","根拠・注意事項"];
  const outputHeaders = ["店舗ID","店舗名","作成ゲート","不足情報・質問","要件定義書ドラフト（AI案）","レビュー判定","修正・追加依頼","最終版URL（任意）","次工程移行","登録日時"];
  const lock = LockService.getDocumentLock();
  if (!lock || !lock.tryLock(30000)) throw new Error("処理が実行中です。");
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    if (!ss || ss.getName() !== expectedName) throw new Error("検証用台帳以外では実行しません。");
    const q = ss.getSheetByName("LP要件定義キュー");
    const out = ss.getSheetByName("LP要件定義レビュー");
    const intake = ss.getSheetByName("LP制作入力");
    if (!q || !out || !intake) throw new Error("必要なシートが不足しています。");
    const matches = (actual,expected) => expected.every((v,i)=>actual[i]===v);
    if (!matches(q.getRange(1,1,1,8).getDisplayValues()[0],inputHeaders) ||
        !matches(out.getRange(1,1,1,10).getDisplayValues()[0],outputHeaders)) {
      throw new Error("ヘッダーが異なるため、書き込みを停止しました。");
    }
    const expectedConsentColumn = intake.getRange(1,9).getDisplayValue();
    if (expectedConsentColumn !== "制作許可") throw new Error("制作許可の列が想定と異なります。");
    const intakeRows = intake.getLastRow()>1
      ? intake.getRange(2,1,intake.getLastRow()-1,10).getDisplayValues():[];
    const permissions = new Map(intakeRows.filter(r=>r[0]).map(r=>[r[0].trim(),r[8].trim()]));
    const existing = new Set();
    if (out.getLastRow()>1) {
      out.getRange(2,1,out.getLastRow()-1,1).getDisplayValues()
        .forEach(r=>{if(r[0].trim())existing.add(r[0].trim());});
    }
    const queued = q.getLastRow()>1
      ? q.getRange(2,1,q.getLastRow()-1,8).getDisplayValues():[];
    const newRows=[];
    let skipped=0, blocked=0;
    queued.forEach(r=>{
      const id=r[0].trim();
      if (!id) return;
      if (existing.has(id)){skipped++;return;}
      const permitted=permissions.get(id)==="確認済み";
      const gate=permitted
        ? "制作許可確認済：不足情報を人間が確認"
        : "制作許可未確認：AIドラフト生成禁止";
      if(!permitted)blocked++;
      newRows.push([id,r[1],gate,r[3],"","未確認","","","不可",new Date()]);
      existing.add(id);
    });
    if(newRows.length) {
      const start=out.getLastRow()+1;
      out.getRange(start,1,newRows.length,10).setValues(newRows);
      out.getRange(start,4,newRows.length,4).setWrap(true);
      out.getRange(start,10,newRows.length,1).setNumberFormat("yyyy/mm/dd hh:mm");
    }
    console.log("=== LP要件定義レビュー同期 ===");
    console.log("新規レビュー登録："+newRows.length+"件");
    console.log("既存IDのためスキップ："+skipped+"件");
    console.log("今回登録分で制作許可未確認："+blocked+"件");
    console.log("AI API呼出し・実装・GitHub公開：なし");
  } finally {lock.releaseLock();}
}
