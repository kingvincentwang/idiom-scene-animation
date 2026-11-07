# idiom-scene-animation

Claude Code skill：把成語故事做成分幕動畫網頁。用 Gemini 生成插圖當場景，加上鏡頭推移、對白泡泡、字幕、繁體中文語音旁白、Web Audio 合成音效，以及角色說話時配合旁白開合的口形。成品是單一 HTML 檔，雙擊就能播放，也能放上 GitHub Pages。

使用方式與完整流程見 [SKILL.md](SKILL.md)。

## 安裝

```bash
git clone https://github.com/kingvincentwang/idiom-scene-animation.git ~/.claude/skills/idiom-scene-animation
```

需要 Python 與 Pillow（輔助腳本使用）。插圖用 Gemini 網頁版生成，需要 Google 帳號。

## 內容

| 檔案 | 用途 |
|---|---|
| `assets/template.html` | 範本：〈指鹿為馬〉的完整動畫（6 幕、口形、音效） |
| `scripts/grid_crop.py` | 放大圖片局部並加上格線，用來讀出角色嘴巴的座標 |
| `scripts/check_mouths.py` | 把動畫裡每張嘴以閉、半開、全開畫到插圖上，拼成一張總覽來檢查位置 |

範本不附插圖。使用時，在成語資料夾的 `images/` 放入 `scene1.jpg`～`sceneN.jpg` 與角色設定圖 `char_*.jpg`。

## 注意

旁白使用瀏覽器內建語音，在不同電腦或瀏覽器播放時聲音可能不同。需要固定聲音時，可依 SKILL.md 改用 edge-tts 預錄的音檔。
