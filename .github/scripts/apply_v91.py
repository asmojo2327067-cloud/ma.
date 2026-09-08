from pathlib import Path
import base64, subprocess, tempfile, os

patch = base64.b64decode("""LS0tIGEvaW5kZXguaHRtbAorKysgYi9pbmRleC5odG1sCkBAIC0zLDcgKzMsNyBAQAogPGhlYWQ+CiA8bWV0YSBjaGFyc2V0PSJVVEYtOCI+CiA8bWV0YSBuYW1lPSJ2aWV3cG9ydCIgY29udGVudD0id2lkdGg9ZGV2aWNlLXdpZHRoLCBpbml0aWFsLXNjYWxlPTEsIG1heGltdW0tc2NhbGU9MSwgdXNlci1zY2FsYWJsZT1ubywgdmlld3BvcnQtZml0PWNvdmVyIj4KLTx0aXRsZT5tYS7vvZzmoYjku7Ygdjg5PC90aXRsZT4KKzx0aXRsZT5tYS7vvZzmoYjku7YgdjkxPC90aXRsZT4KIDxzdHlsZT4KIDpyb290ewogICAtLWJnOiNmM2YyZWU7CkBAIC00MzY1LDkgKzQzNjUsNDUgQEAKICAgfQogfQogCisKKy8qID09PT09IG1hLiB2OTAgLyBpbGx1c3RyYXRpb24gaXMgZGlzcGxheS1vbmx5ID09PT09ICovCisjY2FiaW5ldCwKKyNjYWJpbmV0ICosCisjc2tldGNoVmlldywKKyNza2V0Y2hWaWV3ICp7CisgIHBvaW50ZXItZXZlbnRzOm5vbmUhaW1wb3J0YW50OworICBjdXJzb3I6ZGVmYXVsdCFpbXBvcnRhbnQ7Cit9CisKKworLyogPT09PT0gbWEuIHY5MSAvIGlubmVyIGJhY2tib2FyZCBiZWxvbmdzIHRvIEJhY2tib2FyZCB0YWIgPT09PT0gKi8KKyNsZWZ0QmFja2JvYXJkU2VjdGlvbiAuaW5uZXJCYWNrTW92ZWR7CisgIG1hcmdpbi10b3A6MTJweDsKKyAgcGFkZGluZy10b3A6MTBweDsKKyAgYm9yZGVyLXRvcDoxcHggc29saWQgdmFyKC0tbGluZVNvZnQpOworfQorI2xlZnRCYWNrYm9hcmRTZWN0aW9uIC5kb2NrU3ViU2VjdGlvblRpdGxleworICBkaXNwbGF5OmZsZXg7CisgIGFsaWduLWl0ZW1zOmJhc2VsaW5lOworICBqdXN0aWZ5LWNvbnRlbnQ6c3BhY2UtYmV0d2VlbjsKKyAgZ2FwOjEwcHg7CisgIG1hcmdpbi1ib3R0b206N3B4OworfQorI2xlZnRCYWNrYm9hcmRTZWN0aW9uIC5kb2NrU3ViU2VjdGlvblRpdGxlIHN0cm9uZ3sKKyAgZm9udC1zaXplOjExcHg7CisgIGNvbG9yOnZhcigtLWluayk7Cit9CisjbGVmdEJhY2tib2FyZFNlY3Rpb24gLmRvY2tTdWJTZWN0aW9uVGl0bGUgc3BhbnsKKyAgZm9udC1zaXplOjhweDsKKyAgY29sb3I6dmFyKC0tbXV0ZWQpOworfQorI2xlZnRCYWNrYm9hcmRTZWN0aW9uIC5pbm5lckJhY2tDb250cm9sc3sKKyAgbWFyZ2luLXRvcDowIWltcG9ydGFudDsKK30KKwogPC9zdHlsZT4KIDwvaGVhZD4KLTxib2R5IGRhdGEtYnVpbGQ9Im1hLXByb2plY3Qtdjg5IiBjbGFzcz0icGFnZS1ob21lIj4KKzxib2R5IGRhdGEtYnVpbGQ9Im1hLXByb2plY3QtdjkxIiBjbGFzcz0icGFnZS1ob21lIj4KIDxkaXYgY2xhc3M9InBhcGVyVGV4dHVyZSIgYXJpYS1oaWRkZW49InRydWUiPjwvZGl2PgogCiA8bmF2IGNsYXNzPSJkZXNrdG9wTmF2IiBhcmlhLWxhYmVsPSLjg6HjgqTjg7Pjg4rjg5PjgrLjg7zjgrfjg6fjg7MiPgpAQCAtNDc4MywxNCArNDgxOSwxNCBAQAogICAgICAgICAgIDxkaXYgY2xhc3M9ImRvY2tDb250ZXh0TWFpbiI+CiAgICAgICAgICAgICA8c3BhbiBjbGFzcz0iZG9ja0NvbnRleHRFeWVicm93Ij7pgbjmip7kuK08L3NwYW4+CiAgICAgICAgICAgICA8c3Ryb25nIGlkPSJkb2NrQ29udGV4dFRpdGxlIj7lpJbnrrE8L3N0cm9uZz4KLSAgICAgICAgICAgIDxzcGFuIGlkPSJkb2NrQ29udGV4dEhpbnQiPuWbs+mdouOBrumDqOadkOOChOWMuueUu+OCkuOCv+ODg+ODl+OBmeOCi+OBqOOAgeOBneOBruioreWumuOCkumWi+OBjeOBvuOBmeOAgjwvc3Bhbj4KKyAgICAgICAgICAgIDxzcGFuIGlkPSJkb2NrQ29udGV4dEhpbnQiPuioreWumuOBr+S4i+OBruOCv+ODluOBi+OCiemBuOOBs+OBvuOBmeOAgjwvc3Bhbj4KICAgICAgICAgICA8L2Rpdj4KICAgICAgICAgICA8YnV0dG9uIGlkPSJkb2NrQ29udGV4dENsb3NlIiBjbGFzcz0iZG9ja0NvbnRleHRDbG9zZSIgdHlwZT0iYnV0dG9uIiBhcmlhLWxhYmVsPSLoqK3lrprjgrfjg7zjg4jjgpLplonjgZjjgosiPsOXPC9idXR0b24+CiAgICAgICAgIDwvZGl2PgogICAgICAgICA8ZGl2IGNsYXNzPSJ3b3Jrc3BhY2VEb2NrQmFyIj4KICAgICAgICAgICA8ZGl2IGNsYXNzPSJ3b3Jrc3BhY2VEb2NrVGFicyIgcm9sZT0idGFibGlzdCIgYXJpYS1sYWJlbD0i57SN44G+44KKIj4KICAgICAgICAgICAgIDxidXR0b24gdHlwZT0iYnV0dG9uIiBjbGFzcz0iYWN0aXZlIiBkYXRhLXdvcmtzcGFjZS1kb2NrLXRhYj0iYm94IiByb2xlPSJ0YWIiPueuseOBruani+aIkDwvYnV0dG9uPgotICAgICAgICAgICAgPGJ1dHRvbiB0eXBlPSJidXR0b24iIGRhdGEtd29ya3NwYWNlLWRvY2stdGFiPSJyZWdpb24iIHJvbGU9InRhYiI+5Yy655S7PC9idXR0b24+CisgICAgICAgICAgICA8YnV0dG9uIHR5cGU9ImJ1dHRvbiIgZGF0YS13b3Jrc3BhY2UtZG9jay10YWI9InJlZ2lvbiIgcm9sZT0idGFiIj7mo5rjg7vmnZ88L2J1dHRvbj4KICAgICAgICAgICAgIDxidXR0b24gdHlwZT0iYnV0dG9uIiBkYXRhLXdvcmtzcGFjZS1kb2NrLXRhYj0iam9pbnQiIHJvbGU9InRhYiI+5Zub6ZqFPC9idXR0b24+CiAgICAgICAgICAgICA8YnV0dHRvbiB0eXBlPSJidXR0b24iIGRhdGEtd29ya3NwYWNlLWRvY2stdGFiPSJwbGludGgiIHJvbGU9InRhYiI+5be+5pyoPC9idXR0b24+CiAgICAgICAgICAgICA8YnV0dHRvbiB0eXBlPSJidXR0b24iIGRhdGEtd29ya3NwYWNlLWRvY2stdGFiPSJiYWNrYm9hcmQiIHJvbGU9InRhYiI+6IOM5p2/PC9idXR0b24+CiAgICAgICAgICA8L2Rpdj4KICAgICAgICAgIDxkaXYgY2xhc3M9IndvcmtzcGFjZURvY2tIaW50Ij7jg4njg6njg4PjgrDjgafpq5jjgZXoqr/jgIDvvI8g44OA44OW44Or44Kv44Oq44OD44Kv44Gn5oqY44KK44Gf44Gf44G/PC9kaXY+CiAgICAgICAgPC9kaXY+CiAgICAgICAgPGRpdiBjbGFzcz0id29ya3NwYWNlRG9ja0JvZHkiPgoKICAgICAgICAgIDxzZWN0aW9uIGNsYXNzPSJ3b3Jrc3BhY2VEb2NrUGFuZWwgYWN0aXZlIiBkYXRhLXdvcmtzcGFjZS1kb2NrLXBhbmVsPSJib3giPgoKICAgICAgICAgIDxzZWN0aW9uIGNsYXNzPSJ3b3Jrc3BhY2VEb2NrUGFuZWwiIGRhdGEtd29ya3NwYWNlLWRvY2stcGFuZWw9InJlZ2lvbiI+CiAgPGRpdiBjbGFzcz0ic2VjdGlvbiBzaWRlUGFuZWwgZG9ja1JlZ2lvblN0cnVjdHVyZSIgaWQ9ImxlZnRSZWdpb25TZWN0aW9uIj4KICAgIDxoMz7pgbjmip7kuK3jga7ljLrnlLs8L2gzPgogICAgPGRpdiBpZD0ic2VsZWN0ZWRJbmZvIiBjbGFzcz0ic2VsZWN0ZWRCb3giPuWklueusTwvZGl2PgoKICAgIDxkaXYgY2xhc3M9ImZpZWxkIj4KICAgICAgPGxhYmVsPui/veWKoOaemuaVsDwvbGFiZWw+CiAgICAgIDxkaXYgY2xhc3M9InN0ZXAiPgogICAgICAgIDxidXR0b24gaWQ9ImNvdW50TWludXMiPuKIiTwvYnV0dG9uPgogICAgICAgIDxpbnB1dCBpZD0iYWRkQ291bnQiIHR5cGU9Im51bWJlciIgdmFsdWU9IjEiIG1pbj0iMSI+CiAgICAgICAgPGJ1dHRvbiBpZD0iY291bnRQbHVzIj7vvIs8L2J1dHRvbj4KICAgICAgPC9kaXY+CiAgICA8L2Rpdj4KCiAgICA8ZGl2IGNsYXNzPSJmaWVsZCI+CiAgICAgIDxsYWJlbD7phY3nva48L2xhYmVsPgogICAgICA8ZGl2IGNsYXNzPSJzZWcgdGhyZWUiIGlkPSJwbGFjZU1vZGUiPgogICAgICAgIDxidXR0b24gZGF0YS12YWx1ZT0iZXF1YWwiIGNsYXNzPSJhY3RpdmUiPuetieWIhjwvYnV0dG9uPgogICAgICAgIDxidXR0b24gZGF0YS12YWx1ZT0iY2xlYXIiPuaacieKue+8iDwvaHRtbD4KICAgICAgICA8YnV0dG9uIGRhdGEtdmFsdWU9ImZyb20iPuWkluOBi+OCiTwvYnV0dG9uPgogICAgICA8L2Rpdj4KICAgIDwvZGl2PgoKICAgIDxkaXYgY2xhc3M9ImZpZWxkIj4KICAgICAgPGxhYmVsPuaoquWQkeOBruWfuua6ljwvbGFiZWw+CiAgICAgIDxkaXYgY2xhc3M9InNlZyIgaWQ9Imhvcml6b250YWxBeGlzUmVmIj4KICAgICAgICA8YnV0dG9uIGRhdGEtdmFsdWU9ImxlZnQiIGNsYXNzPSJhY3RpdmUiPuW3puOBi+OCiTwvYnV0dG9uPgogICAgICAgIDxidXR0b24gZGF0YS12YWx1ZT0icmlnaHQiPuWPs+OBi+OCiTwvYnV0dG9uPgogICAgICA8L2Rpdj4KICAgIDwvZGl2PgoKICAgIDxkaXYgY2xhc3M9ImZpZWxkIj4KICAgICAgPGxhYmVsPuOCs+ODs+ODhuODs+ODhOWQkeOBruWfuua6ljwvbGFiZWw+CiAgICAgIDxkaXYgY2xhc3M9InNlZyIgaWQ9InZlcnRpY2FsQXhpc1JlZiI+CiAgICAgICAgPGJ1dHRvbiBkYXRhLXZhbHVlPSJ0b3AiIGNsYXNzPSJhY3RpdmUiPuS4iuOBi+OCiTwvYnV0dG9uPgogICAgICAgIDxidXR0b24gZGF0YS12YWx1ZT0iYm90dG9tIj7kuIvjgYvjgok8L2J1dHRvbj4KICAgICAgPC9kaXY+CiAgICA8L2Rpdj4KCiAgICA8ZGl2IGlkPSJwbGFjZURldGFpbCIgY2xhc3M9ImhpZGRlbiI+CiAgICAgIDxkaXYgY2xhc3M9ImZpZWxkIj4KICAgICAgICA8bGFiZWw+5L2N572u44O75pyJ5Yq544Gu5byPPC9sYWJlbD4KICAgICAgICA8aW5wdXQgaWQ9InBsYWNlRm9ybXVsYSIgdHlwZT0idGV4dCIgdmFsdWU9IjYwMCIgcGxhY2Vob2xkZXI9IuS+iTogNjAwIC8gVy8zIC8gSC8yIj4KICAgICAgPC9kaXY+CiAgICA8L2Rpdj4KCiAgICA8ZGl2IGNsYXNzPSJhZGRCdXR0b25zIj4KICAgICAgPGJ1dHRvbiBpZD0iYWRkRGl2aWRlciI+77yLIOadnyDvvIjnq5njgIkiPC9idXR0b24+CiAgICAgIDxidXR0b24gaWQ9ImFkZFNoZWxmIj7vvIsg5qOa77yI5qiq77yJPC9idXR0b24+CiAgICA8L2Rpdj4KICAgIDxwIGNsYXNzPSJub3RlIj7mqKrln7rmuZbjgajjg4Pjg6Ljg6Pjg7Pjga/jgYTjgaTjgoLkv53mjIHjgZfjgb7jgZnjgILjgIzmnInlirnjgI3jgIzlpJbjgYvjgonnrYnjgaflhaXlipvjgZfjgZ/m 数値・式は構造図と3Dの位置に反映します。</p>
    <button id="undoSplit" class="ghost danger" style="width:100%;margin-top:8px">選択区画の分割を戻す</button>
  </div>

          </section>

          <section class="workspaceDockPanel" data-workspace-dock-panel="joint">
            <div class="dockJointStage jointTextStage">
              <div class="dockPanelTitle"><strong>四隅の納まり</strong><span>文字をクリックして切替</span></div>
              <div id="jointDetails" class="jointTextGrid" aria-label="四隅の納まり"></div>
            </div>
          </section>

          <section class="workspaceDockPanel" data-workspace-dock-panel="plinth">
            <div class="dockSplitLayout dockPlinthLayout">
              <div class="dockIllustration">
                <div class="dockPanelTitle"><strong>巾木</strong><span>辺をクリックして ON / OFF</span></div>
                <svg viewBox="0 0 260 190" aria-label="巾木平面"><g id="plinthPlan"></g></svg>
              </div>
              <div class="section dockSettingsPanel" id="leftPlinthSection">
    <div class="switchRow">
      <div>
        <h3 style="margin-bottom:2px">巾木</h3>
        <div class="note">前勝ち → 横負け / 横勝ち → 後ろ負け</div>
      </div>
      <button id="plinthToggle" class="toggleBtn">なし</button>
    </div>
    <div id="plinthFields" class="hidden plinthSingleFields">
      <div class="field">
        <label>作る辺</label>
        <div class="edgeGrid">
          <button class="edgeBtn on" data-plinth-edge="front">前</button>
          <button class="edgeBtn on" data-plinth-edge="left">左</button>
          <button class="edgeBtn on" data-plinth-edge="right">右</button>
          <button class="edgeBtn" data-plinth-edge="back">後</button>
        </div>
      </div>
      <div class="plinthSixGrid">
        <div class="field">
          <label>高さ</label>
          <input id="plinthHeight" type="text" value="60">
        </div>
        <div class="field">
          <label>前引き</label>
          <input id="plinthFrontSetback" type="text" value="50">
        </div>
        <div class="field">
          <label>横引き</label>
          <input id="plinthSideSetback" type="text" value="0">
        </div>
        <div class="field">
          <label>後引き</label>
          <input id="plinthBackSetback" type="text" value="0">
        </div>
        <div class="field">
          <label>横奥行</label>
          <input id="plinthSideDepth" type="text" value="100">
        </div>
        <div class="field plinthWideField">
          <label>側板下端</label>
          <div class="seg" id="plinthSideDrop">
            <button data-value="body" class="active">地板ライン</button>
            <button data-value="plinth">巾木下端</button>
          </div>
        </div>
      </div>
    </div>
  </div>
            </div>
          </section>

          <section class="workspaceDockPanel" data-workspace-dock-panel="backboard">
            <div class="dockSplitLayout dockBackboardLayout">
              <div class="dockIllustration">
                <div class="dockPanelTitle"><strong>背板断面</strong><span>右の設定を表示</span></div>
                <svg viewBox="0 0 320 250" aria-label="背板断面">
                  <g id="backboardDetail"></g>
                  <g id="innerBackboardDetail"></g>
                </svg>
              </div>
              <div class="section dockSettingsPanel" id="leftBackboardSection">
    <div class="switchRow">
      <div>
        <h3 style="margin-bottom:3px">背板</h3>
        <div class="note">箱との納まりを3種類から選択</div>
      </div>
      <button id="backboardToggle" class="toggleBtn">なし</button>
    </div>
    <div id="backboardFields" class="hidden">
      <div class="field">
        <label>背板の納まり</label>
        <div class="seg three" id="backboardMode">
          <button data-value="inside" class="active">内収まり</button>
          <button data-value="inset5">四周5mm</button>
          <button data-value="outside">外貼り</button>
        </div>
      </div>
      <div id="backboardModeNote" class="selectedBox" style="margin-top:9px">箱の内側に収まるサイズ</div>
      <p class="note">外貼りのときも外寸 D は変えません。箱本体・束・棚の奥行は <strong>D - 背板厚</strong> として扱います。</p>

    <div class="innerBackMoved">
      <div class="dockSubSectionTitle">
        <strong>内背</strong>
        <span>選択区画ごと</span>
      </div>
    <div class="innerBackControls">
      <div class="row">
        <div>
          <strong style="font-size:12px">区画の内背板</strong>
          <div class="note">選択区画ごとに設定</div>
        </div>
        <button id="innerBackToggle" class="toggleBtn">＋ 内背板</button>
      </div>
      <div id="innerBackFields" class="hidden">
        <div class="field">
          <label>奥行位置の基準</label>
          <div class="seg" id="innerBackRef">
            <button data-value="front">前から</button>
            <button data-value="back" class="active">後ろから</button>
          </div>
        </div>
        <div class="field">
          <label>基準からの位置・式</label>
          <input id="innerBackFormula" type="text" value="50" placeholder="例: 50 / D/4">
        </div>
        <div id="innerBackStatus" class="note" style="margin-top:7px"></div>
      </div>
    </div>
    </div>
    </div>
  </div>
            </div>
          </section>
        </div>
      </section>

    </div>
  </div>
</main>

<aside class="right">
  <div class="section historySection sidePanel rightPartsOnly" id="rightHistorySection">
    <div class="historyHeading">
      <div>
        <h3>部材</h3>
        <p class="note">構造からの自動部材と、図に出ない追加部材をまとめて管理します。</p>
      </div>
      <button id="addCustomPart" class="historyAddPartButton" type="button">＋ 部材を追加</button>
    </div>
    <div id="tree" class="historyList"></div>
    <div id="historyEditor" class="historyEditor"></div>
  </div>

</aside>

</div>

<div id="mobileFlow" class="mobileFlow" aria-label="スマホ専用編集UI"></div>

<div id="mobileSidebarBackdrop" class="mobileSidebarBackdrop" hidden></div>

<div id="mobileSidebarHandles" class="mobileSidebarHandles" aria-hidden="true">
  <span id="mobileLeftEdgeBar" class="mobileEdgeBar mobileEdgeBarLeft"></span>
  <span id="mobileRightEdgeBar" class="mobileEdgeBar mobileEdgeBarRight"></span>
</div>

<aside id="mobileLeftSidebar" class="mobileSidebar mobileSidebarLeft" aria-hidden="true" aria-label="データサイドバー">
  <div class="mobileSidebarHead">
    <div><strong>データ</strong><span>master / dimensions</span></div>
    <button type="button" data-mobile-sidebar-close aria-label="データサイドバーを閉じる">×</button>
  </div>
  <div id="mobileLeftSidebarBody" class="mobileSidebarBody"></div>
</aside>

<aside id="mobileRightSidebar" class="mobileSidebar mobileSidebarRight" aria-hidden="true" aria-label="部材サイドバー">
  <div class="mobileSidebarHead">
    <div><strong>部材</strong><span>all parts</span></div>
    <button type="button" data-mobile-sidebar-close aria-label="部材サイドバーを閉じる">×</button>
  </div>
  <div id="mobileRightSidebarBody" class="mobileSidebarBody"></div>
</aside>

<div id="legacyRegionContentHost" hidden aria-hidden="true">
            <div class="regionContentPanel">
              <div class="regionContentHead">
                <div>
                  <strong id="regionContentTitle">R1 区画構成</strong>
                  <span id="regionContentHint">正面図の区画をクリックして編集</span>
                </div>
              </div>
              <div id="regionContentDisabled" class="regionContentDisabled hidden">分割済みの区画です。中の区画を選択してください。</div>
              <div id="regionContentCards" class="regionContentCards">
                <div class="regionContentCard">
                  <div class="regionContentCardHead">
                    <strong>可動棚</strong>
                    <button id="movShelfToggle" class="miniToggle" type="button">なし</button>
                  </div>
                  <div class="regionContentFields">
                    <label>枚数 <input id="movShelfCount" type="number" min="1" max="12" value="2"></label>
                    <label>前引き <input id="movShelfSetback" type="text" value="20"><span>mm / 式</span></label>
                  </div>
                  <div class="regionContentNote">区画は分割せず、可動棚として部材化</div>
                </div>

                <div class="regionContentCard">
                  <div class="regionContentCardHead">
                    <strong>抽斗</strong>
                    <button id="drawerToggle" class="miniToggle" type="button">なし</button>
                  </div>
                  <div class="regionContentFields">
                    <label>段数 <input id="drawerCount" type="number" min="1" max="12" value="3"></label>
                    <div class="regionMiniSeg" id="drawerFit">
                      <button type="button" data-value="inside" class="active">内収まり</button>
                      <button type="button" data-value="overlay">かぶせ</button>
                    </div>
                    <label><span id="drawerAllowanceLabel">隙間</span> <input id="drawerAllowance" type="text" value="2"><span>mm / 式</span></label>
                  </div>
                  <div class="regionContentNote">現段階は前板を自動部材化。抽斗箱は次の詳細設定で追加</div>
                </div>

                <div class="regionContentCard">
                  <div class="regionContentCardHead">
                    <strong>扉</strong>
                    <button id="doorToggle" class="miniToggle" type="button">なし</button>
                  </div>
                  <div class="regionMiniSeg three" id="doorType">
                    <button type="button" data-value="left" class="active">左吊元</button>
                    <button type="button" data-value="right">右吊元</button>
                    <button type="button" data-value="double">両開き</button>
                  </div>
                  <div class="regionMiniSeg" id="doorFit">
                    <button type="button" data-value="inside" class="active">内収まり</button>
                    <button type="button" data-value="overlay">かぶせ</button>
                  </div>
                  <label class="regionAllowance"><span id="doorAllowanceLabel">隙間</span> <input id="doorAllowance" type="text" value="2"><span>mm / 式</span></label>
                </div>
              </div>
            </div>
          </div>
<div id="mobileInputToolbar" class="mobileInputToolbar" hidden aria-label="入力移動">
  <button id="mobileInputPrev" type="button">前へ</button>
  <button id="mobileInputNext" type="button">次へ</button>
  <button id="mobileInputDone" type="button">完了</button>
</div>

<script>
const state={
  outer:{W:1800,H:900,D:450},
  outerFormula:{W:"1800",H:"900",D:"450"},
  joints:{tl:"side",tr:"side",bl:"side",br:"side"},
  selected:"R1",
  root:{id:"R1",split:null,innerBackboard:null},
  nextRegion:2,
  nextPart:1,
  nextHistory:1,
  historySelection:"",
  selectedPartId:null,
  parts:[],
  customParts:[],
  nextCustomPart:1,
  partNames:{},
  partGrain:{},
  overrides:{},
  placeMode:"equal",
  horizontalRef:"left",
  verticalRef:"top",
  placeFormula:"600",
  plinth:{enabled:false,heightFormula:"60",front:true,left:true,right:true,back:false,frontSetbackFormula:"50",sideSetbackFormula:"0",backSetbackFormula:"0",sideDepthFormula:"100",sideDrop:{left:"body",right:"body"}},
  backboard:{enabled:true,mode:"inside"},
  innerBox:{top:"none",sides:"none",bottom:"none",gapFormula:"0"},
  materials:[
    {id:"MDF18",name:"MDF18",partNo:"",type:"core",thickness:18,sheet:{preset:"3x6",w:1820,h:910},species:"",grain:"none"},
    {id:"MDF15",name:"MDF15",partNo:"",type:"core",thickness:15,sheet:{preset:"3x6",w:1820,h:910},species:"",grain:"none"},
    {id:"PLY12",name:"ラワン合板12",partNo:"",type:"core",thickness:12,sheet:{preset:"3x6",w:1820,h:910},species:"ラワン",grain:"long"},
    {id:"PLY9",name:"ラワン合板9",partNo:"",type:"core",thickness:9,sheet:{preset:"3x6",w:1820,h:910},species:"ラワン",grain:"long"},
    {id:"PLY5.5",name:"ラワン合板5.5",partNo:"",type:"core",thickness:5.5,sheet:{preset:"3x6",w:1820,h:910},species:"ラワン",grain:"long"},
    {id:"MDF4",name:"MDF4",partNo:"",type:"core",thickness:4,sheet:{preset:"3x6",w:1820,h:910},species:"",grain:"none"},
    {id:"PLY4",name:"ラワン合板4",partNo:"",type:"core",thickness:4,sheet:{preset:"3x6",w:1820,h:910},species:"ラワン",grain:"long"},
    {id:"MDF3",name:"MDF3",partNo:"",type:"core",thickness:3,sheet:{preset:"3x6",w:1820,h:910},species:"",grain:"none"},
    {id:"POLY2.5",name:"ポリ板2.5",partNo:"",type:"finish",thickness:2.5,sheet:{preset:"3x6",w:1820,h:910},species:"",grain:"long"},
    {id:"VENEER0.5",name:"突板0.5",partNo:"",type:"finish",thickness:0.5,sheet:{preset:"3x6",w:1820,h:910},species:"",grain:"long"}
  ],
  compositions:[
    {id:"COMP_MDF18",name:"MDF18 素地",coreLayers:[{materialId:"MDF18",count:1}],faceMaterialId:null,backMaterialId:null},
    {id:"COMP_MDF15",name:"MDF15 素地",coreLayers:[{materialId:"MDF15",count:1}],faceMaterialId:null,backMaterialId:null},
    {id:"COMP_PLY12",name:"ラワン合板12 素地",coreLayers:[{materialId:"PLY12",count:1}],faceMaterialId:null,backMaterialId:null},
    {id:"COMP_MDF4",name:"MDF4 素地",coreLayers:[{materialId:"MDF4",count:1}],faceMaterialId:null,backMaterialId:null},
    {id:"COMP_PLY4",name:"ラワン合板4 素地",coreLayers:[{materialId:"PLY4",count:1}],faceMaterialId:null,backMaterialId:null}
  ],
  defaultCompositionId:"COMP_MDF18",
  partComposition:{},
  partDepthFormula:{},
  unitName:"ユニット 01",
  selectedView:"diagram",
  show3D:false,
  threeView:"front",
  leftTab:"dimensions",
  regionContents:{},
};

const $=id=>document.getElementById(id);
const mm=v=>Number.isFinite(v)?Math.round(v*10)/10:"-";
function thicknessSymbolName(label){return `${label}厚`}
function safeNumber(v,fallback=0){const n=Number(v);return Number.isFinite(n)?n:fallback}
function clamp(v,min,max){return Math.max(min,Math.min(max,v))}

const SHEET_PRESETS={
  "3x6":{label:"3×6",w:1820,h:910},
  "4x8":{label:"4×8",w:2430,h:1220},
  "3x8":{label:"3×8",w:2430,h:910},
  "4x6":{label:"4×6",w:1820,h:1220},
  "4x10":{label:"4×10",w:3050,h:1220},
  custom:{label:"カスタム",w:1820,h:910},
};

const SYMBOL_DEFAULT_THICKNESS={
  "左側板厚":18,"右側板厚":18,"天板厚":18,"地板厚":18,"束厚":18,"棚板厚":18,"巾木厚":18,"背板厚":4,"内背板厚":4,
  "内天板厚":18,"左内側板厚":18,"右内側板厚":18,"内地板厚":18,
};

function materialById(id){return state.materials.find(m=>m.id===id)||null}
function compositionById(id){return state.compositions.find(c=>c.id===id)||null}
function materialThickness(id){return safeNumber(materialById(id)?.thickness,0)}
function compositionThickness(compId){
  const comp=compositionById(compId);
  if(!comp)return 0;
  const core=(comp.coreLayers||[]).reduce((sum,layer)=>sum+materialThickness(layer.materialId)*Math.max(1,safeNumber(layer.count,1)),0);
  return core+materialThickness(comp.faceMaterialId)+materialThickness(comp.backMaterialId);
}
function partCompositionId(partId){
  return state.partComposition[partId]||state.defaultCompositionId||state.compositions[0]?.id||null;
}
function partThickness(partId,fallback=18){
  const t=compositionThickness(partCompositionId(partId));
  return t>0?t:fallback;
}

function symbolThickness(symbol){
  const s=String(symbol||"");
  if(s==="左側板厚")return partThickness("LEFT",18);
  if(s==="右側板厚")return partThickness("RIGHT",18);
  if(s==="天板厚")return partThickness("TOP",18);
  if(s==="地板厚")return partThickness("BOTTOM",18);
  if(s==="巾木厚")return partThickness("PLINTH_FRONT",18);
  if(s==="背板厚")return partThickness("BACKBOARD",4);
  if(s==="内天板厚")return partThickness("INNER_TOP",18);
  if(s==="左内側板厚")return partThickness("INNER_LEFT",18);
  if(s==="右内側板厚")return partThickness("INNER_RIGHT",18);
  if(s==="内地板厚")return partThickness("INNER_BOTTOM",18);
  if(s==="束厚"){
    const p=allPartNodes(state.root).find(x=>x.kind==="split"&&x.orientation==="vertical")?.partId;
    return p?partThickness(p,18):18;
  }
  if(s==="棚板厚"){
    const p=allPartNodes(state.root).find(x=>x.kind==="split"&&x.orientation==="horizontal")?.partId;
    return p?partThickness(p,18):18;
  }
  if(s==="内背板厚"){
    const p=allRegionNodes(state.root).find(r=>r.innerBackboard)?.innerBackboard?.partId;
    return p?partThickness(p,4):4;
  }
  return SYMBOL_DEFAULT_THICKNESS[s]??18;
}

function normalizeExpression(expr){
  return String(expr??"")
    .replace(/[××]/g,"*")
    .replace(/[÷]/g,"/")
    .replace(/[－−ー]/g,"-")
    .replace(/[＋]/g,"+")
    .replace(/[（）]/g,c=>c==="（"?"(":")")
    .replace(/\s+/g,"");
}
function evalFormula(expr,extra={}){
  const normalized=normalizeExpression(expr);
  if(!normalized)return NaN;
  const vars={W:state.outer.W,H:state.outer.H,D:state.outer.D,...extra};
  let src=normalized;
  const thicknessSymbols=Object.keys(SYMBOL_DEFAULT_THICKNESS).sort((a,b)=>b.length-a.length);
  thicknessSymbols.forEach(sym=>{
    src=src.split(sym).join(String(symbolThickness(sym)));
  });
  src=src.replace(/[A-Za-z_][A-Za-z0-9_]*/g,name=>Object.prototype.hasOwnProperty.call(vars,name)?`(${safeNumber(vars[name],0)})`:name);
  if(!/^[0-9+\-*/().]+$/.test(src))return NaN;
  try{
    const result=Function(`"use strict";return (${src})`)();
    return Number.isFinite(result)?result:NaN;
  }catch{return NaN}
}

function jointAt(key){return state.joints[key]}
function leftTopInside(){return jointAt("tl")==="top"?symbolThickness("左側板厚"):0}
function rightTopInside(){return jointAt("tr")==="top"?symbolThickness("右側板厚"):0}
function leftBottomInside(){return jointAt("bl")==="bottom"?symbolThickness("左側板厚"):0}
function rightBottomInside(){return jointAt("br")==="bottom"?symbolThickness("右側板厚"):0}
function topPartWidth(){return state.outer.W-(jointAt("tl")==="side"?symbolThickness("左側板厚"):0)-(jointAt("tr")==="side"?symbolThickness("右側板厚"):0)}
function bottomPartWidth(){return state.outer.W-(jointAt("bl")==="side"?symbolThickness("左側板厚"):0)-(jointAt("br")==="side"?symbolThickness("右側板厚"):0)}
function leftPartHeight(){return state.outer.H-(jointAt("tl")==="top"?symbolThickness("天板厚"):0)-(jointAt("bl")==="bottom"?symbolThickness("地板厚"):0)}
function rightPartHeight(){return state.outer.H-(jointAt("tr")==="top"?symbolThickness("天板厚"):0)-(jointAt("br")==="bottom"?symbolThickness("地板厚"):0)}

function innerBoxParts(){
  const rows=[];
  const cfg=state.innerBox||{};
  const topOn=cfg.top&&cfg.top!=="none";
  const bottomOn=cfg.bottom&&cfg.bottom!=="none";
  const leftOn=cfg.sides==="left"||cfg.sides==="both";
  const rightOn=cfg.sides==="right"||cfg.sides==="both";
  const gap=Math.max(0,evalFormula(cfg.gapFormula||"0")||0);
  const leftOuter=symbolThickness("左側板厚");
  const rightOuter=symbolThickness("右側板厚");
  const topOuter=symbolThickness("天板厚");
  const bottomOuter=symbolThickness("地板厚");
  const bodyW=Math.max(1,state.outer.W-leftOuter-rightOuter);
  const bodyH=Math.max(1,state.outer.H-topOuter-bottomOuter);
  const innerLeftT=symbolThickness("左内側板厚");
  const innerRightT=symbolThickness("右内側板厚");
  const innerTopT=symbolThickness("内天板厚");
  const innerBottomT=symbolThickness("内地板厚");
  if(topOn){
    const width=cfg.top==="outer"?bodyW:Math.max(1,bodyW-(leftOn?(gap+innerLeftT):0)-(rightOn?(gap+innerRightT):0));
    rows.push({id:"INNER_TOP",kind:"innerTop",name:"内天板",w:width,h:state.outer.D,thickness:innerTopT});
  }
  if(bottomOn){
    const width=cfg.bottom==="outer"?bodyW:Math.max(1,bodyW-(leftOn?(gap+innerLeftT):0)-(rightOn?(gap+innerRightT):0));
    rows.push({id:"INNER_BOTTOM",kind:"innerBottom",name:"内地板",w:width,h:state.outer.D,thickness:innerBottomT});
  }
  if(leftOn){
    const h=Math.max(1,bodyH-(topOn&&cfg.top==="outer"?innerTopT:0)-(bottomOn&&cfg.bottom==="outer"?innerBottomT:0));
    rows.push({id:"INNER_LEFT",kind:"innerSide",name:"左内側板",w:h,h:state.outer.D,thickness:innerLeftT});
  }
  if(rightOn){
    const h=Math.max(1,bodyH-(topOn&&cfg.top==="outer"?innerTopT:0)-(bottomOn&&cfg.bottom==="outer"?innerBottomT:0));
    rows.push({id:"INNER_RIGHT",kind:"innerSide",name:"右内側板",w:h,h:state.outer.D,thickness:innerRightT});
  }
  return rows;
}

function findRegion(node,id){
  if(!node)return null;
  if(node.id===id)return node;
  if(node.split){for(const child of node.split.children){const hit=findRegion(child,id);if(hit)return hit}}
  return null;
}
function allRegionNodes(node,arr=[]){
  if(!node)return arr;
  arr.push(node);
  if(node.split)node.split.children.forEach(c=>allRegionNodes(c,arr));
  return arr;
}
function allPartNodes(node,arr=[]){
  if(!node)return arr;
  if(node.split)arr.push({kind:"split",...node.split});
  if(node.split)node.split.children.forEach(c=>allPartNodes(c,arr));
  return arr;
}

function nextRegionId(){return `R${state.nextRegion++}`}
function nextPartId(){return `P${state.nextPart++}`}

function selectedRegion(){return findRegion(state.root,state.selected)||state.root}
function canSplitSelected(){const r=selectedRegion();return !!r&&!r.split}

function splitSelected(orientation){
  const r=selectedRegion();
  if(!r||r.split)return;
  r.innerBackboard=null;
  const count=Math.max(1,parseInt($("addCount").value||"1",10)||1);
  const children=Array.from({length:count+1},()=>({id:nextRegionId(),split:null,innerBackboard:null}));
  r.split={orientation,count,mode:state.placeMode,ref:orientation==="vertical"?state.horizontalRef:state.verticalRef,formula:state.placeFormula,partId:nextPartId(),children,seq:state.nextHistory++};
  state.selected=children[0].id;
  update();
}

function undoSelectedSplit(){
  const parent=findParent(state.root,state.selected);
  if(parent?.split){
    parent.split=null;
    state.selected=parent.id;
    update();
    return;
  }
  const r=selectedRegion();
  if(r?.split){r.split=null;update()}
}
function findParent(node,id){
  if(!node?.split)return null;
  for(const child of node.split.children){
    if(child.id===id)return node;
    const hit=findParent(child,id);if(hit)return hit;
  }
  return null;
}

function collectRegions(node,rect,out=[]){
  if(!node)return out;
  out.push({node,...rect});
  if(!node.split)return out;
  const parts=splitGeometry(node.split,rect.w,rect.h);
  parts.regions.forEach((rg,i)=>collectRegions(node.split.children[i],{x:rect.x+rg.x,y:rect.y+rg.y,w:rg.w,h:rg.h},out));
  return out;
}

function splitGeometry(split,w,h){
  const count=Math.max(1,split.count||1);
  const n=count+1;
  const thickness=split.orientation==="vertical"?symbolThickness("束厚"):symbolThickness("棚板厚");
  const axis=split.orientation==="vertical"?w:h;
  const available=Math.max(1,axis-thickness*count);
  let spaces=Array(n).fill(available/n);
  if(split.mode!=="equal"){
    const v=Math.max(0,evalFormula(split.formula,{W:w,H:h,D:state.outer.D})||0);
    const near=split.mode==="clear"?v:Math.max(0,v-thickness/2);
    if(split.ref==="right"||split.ref==="bottom"){
      spaces[n-1]=Math.min(available,near);
      const remaining=Math.max(0,available-spaces[n-1]);
      for(let i=0;i<n-1;i++)spaces[i]=remaining/(n-1);
    }else{
      spaces[0]=Math.min(available,near);
      const remaining=Math.max(0,available-spaces[0]);
      for(let i=1;i<n;i++)spaces[i]=remaining/(n-1);
    }
  }
  const regions=[];
  const cuts=[];
  let cursor=0;
  for(let i=0;i<n;i++){
    const size=spaces[i];
    if(split.orientation==="vertical")regions.push({x:cursor,y:0,w:size,h});
    else regions.push({x:0,y:cursor,w,h:size});
    cursor+=size;
    if(i<count){
      if(split.orientation==="vertical")cuts.push({x:cursor,y:0,w:thickness,h});
      else cuts.push({x:0,y:cursor,w,h:thickness});
      cursor+=thickness;
    }
  }
  return{regions,cuts,spaces};
}

function regionRectById(id){
  const content=interiorRect();
  return collectRegions(state.root,content).find(r=>r.node.id===id)||null;
}

function interiorRect(){
  const left=symbolThickness("左側板厚");
  const right=symbolThickness("右側板厚");
  const top=symbolThickness("天板厚");
  const bottom=symbolThickness("地板厚");
  return{x:left,y:top,w:Math.max(1,state.outer.W-left-right),h:Math.max(1,state.outer.H-top-bottom)};
}

function formulas(){
  const rows=[
    {id:"LEFT",name:"左側板",f1:"H",f2:"D",thickness:symbolThickness("左側板厚")},
    {id:"RIGHT",name:"右側板",f1:"H",f2:"D",thickness:symbolThickness("右側板厚")},
    {id:"TOP",name:"天板",f1:`W${jointAt("tl")==="side"?"-左側板厚":""}${jointAt("tr")==="side"?"-右側板厚":""}`,f2:"D",thickness:symbolThickness("天板厚")},
    {id:"BOTTOM",name:"地板",f1:`W${jointAt("bl")==="side"?"-左側板厚":""}${jointAt("br")==="side"?"-右側板厚":""}`,f2:"D",thickness:symbolThickness("地板厚")},
  ];
  allPartNodes(state.root).forEach(p=>{
    if(p.orientation==="vertical")rows.push({id:p.partId,name:"束",f1:"H-天板厚-地板厚",f2:"D",thickness:partThickness(p.partId,18),qty:p.count});
    else rows.push({id:p.partId,name:"棚板",f1:"W-左側板厚-右側板厚",f2:"D",thickness:partThickness(p.partId,18),qty:p.count});
  });
  innerBoxParts().forEach(p=>rows.push({id:p.id,name:p.name,f1:mm(p.w),f2:mm(p.h),thickness:p.thickness,qty:1}));
  if(state.plinth.enabled){
    if(state.plinth.front)rows.push({id:"PLINTH_FRONT",name:"前巾木",f1:"W",f2:state.plinth.heightFormula,thickness:partThickness("PLINTH_FRONT",18),qty:1});
    if(state.plinth.left)rows.push({id:"PLINTH_LEFT",name:"左巾木",f1:state.plinth.sideDepthFormula,f2:state.plinth.heightFormula,thickness:partThickness("PLINTH_LEFT",18),qty:1});
    if(state.plinth.right)rows.push({id:"PLINTH_RIGHT",name:"右巾木",f1:state.plinth.sideDepthFormula,f2:state.plinth.heightFormula,thickness:partThickness("PLINTH_RIGHT",18),qty:1});
    if(state.plinth.back)rows.push({id:"PLINTH_BACK",name:"後巾木",f1:"W",f2:state.plinth.heightFormula,thickness:partThickness("PLINTH_BACK",18),qty:1});
  }
  if(state.backboard.enabled)rows.push({id:"BACKBOARD",name:"背板",f1:state.backboard.mode==="outside"?"W":"W-左側板厚-右側板厚",f2:state.backboard.mode==="outside"?"H":"H-天板厚-地板厚",thickness:partThickness("BACKBOARD",4),qty:1});
  allRegionNodes(state.root).forEach(r=>{
    if(r.innerBackboard)rows.push({id:r.innerBackboard.partId,name:`内背板 ${r.id}`,f1:`regionW(${r.id})`,f2:`regionH(${r.id})`,thickness:partThickness(r.innerBackboard.partId,4),qty:1});
  });
  state.customParts.forEach(p=>rows.push({id:p.id,name:p.name||"追加部材",f1:p.f1||"W",f2:p.f2||"D",thickness:partThickness(p.id,18),qty:Math.max(1,safeNumber(p.qty,1)),kind:"custom"}));
  return rows;
}

function partDisplayName(partId){
  const custom=state.customParts.find(p=>p.id===partId);
  if(custom)return state.partNames[partId]||custom.name||"追加部材";
  const found=formulas().find(r=>r.id===partId);
  return state.partNames[partId]||found?.name||partId;
}

function partReferenceToken(partId,field){
  const label=partDisplayName(partId);
  return `[${label}#${partId}:${field}]`;
}
function formulaReferenceThickness(partId,rows=formulas()){
  const r=rows.find(x=>x.id===partId);
  if(!r)return NaN;
  const actual=compositionThickness(partCompositionId(partId));
  if(actual>0)return actual;
  return String(partId).startsWith("BACK")||String(partId).startsWith("INNER_BACK")?4:(r.thickness||18);
}
function resolveCutFormula(expr,rows=formulas(),regionMap=null,stack=[]){
  let src=String(expr??"");
  const tokenRe=/\[([^#\]]*)#([^:\]]+):(厚|①|②)\]/g;
  let safety=0;
  while(tokenRe.test(src)&&safety++<30){
    tokenRe.lastIndex=0;
    src=src.replace(tokenRe,(m,label,id,field)=>{
      if(stack.includes(id))return "NaN";
      const target=rows.find(r=>r.id===id);
      if(!target)return "NaN";
      if(field==="厚")return String(formulaReferenceThickness(id,rows));
      const nested=field==="①"?target.f1:target.f2;
      const v=resolveCutFormula(nested,rows,regionMap,[...stack,id]);
      return Number.isFinite(v)?String(v):"NaN";
    });
  }
  if(src.includes("NaN"))return NaN;
  src=src.replace(/regionW\((R\d+)\)/g,(m,id)=>String(regionMap?.[id]?.w??NaN));
  src=src.replace(/regionH\((R\d+)\)/g,(m,id)=>String(regionMap?.[id]?.h??NaN));
  return evalFormula(src);
}

function buildCutRegionMap(rows=formulas()){
  const map={};
  collectRegions(state.root,interiorRect()).forEach(r=>map[r.node.id]={w:r.w,h:r.h});
  return map;
}

function renderFormulaList(){
  const rows=formulas();
  const list=$("tree");
  list.innerHTML="";
  rows.forEach(r=>{
    const item=document.createElement("div");
    item.className=`historyItem${isPartSelected(r.id)?" selectedPartCard":""}`;
    item.dataset.formulaPart=r.id;
    item.innerHTML=`<div class="historySummary"><strong>${escapeHtml(partDisplayName(r.id))}</strong><span>${escapeHtml(r.f1)} × ${escapeHtml(r.f2)}</span></div>`;
    item.addEventListener("click",()=>{state.historySelection=r.id;setSelectedPart(r.id);renderHistoryEditor()});
    list.appendChild(item);
  });
  renderHistoryEditor();
}

function isPartSelected(id){return state.selectedPartId===id}
function setSelectedPart(partId,{rerenderFormula=false}={}){
  state.selectedPartId=partId||null;
  document.querySelectorAll(".formulaCard[data-formula-part]").forEach(card=>{
    card.classList.toggle("selectedPartCard",isPartSelected(card.dataset.formulaPart));
  });
  renderCabinet();
  draw3D();
  if(rerenderFormula)renderFormulaList();
  if(partId){
    const tab=contextualDockTabForPart(partId);
    openContextSettings({
      tab,
      title:contextualPartTitle(partId),
      hint:tab==="region"?"区画の配置・寸法を編集します。":
           tab==="plinth"?"巾木の有無・位置・寸法を編集します。":
           tab==="backboard"?"背板の納まりを編集します。":
           "選択した部材の構成を確認します。"
    });
    focusSelectedFormulaCard(partId);
  }
}

function contextualDockTabForPart(partId){
  const id=String(partId||"");
  if(id.startsWith("PLINTH_")||id==="PLINTH_GROUP")return "plinth";
  if(id==="BACKBOARD"||id.startsWith("INNER_BACK_"))return "backboard";
  if(id.startsWith("DIV_")||id.startsWith("SHELF_")||id.startsWith("MOV_SHELF_"))return "region";
  return "box";
}
function contextualPartTitle(partId){
  if(!partId)return "外箱";
  try{return partDisplayName(partId)||partId}catch(_){return partId}
}
function focusSelectedFormulaCard(partId){
  requestAnimationFrame(()=>{
    const card=[...document.querySelectorAll(".formulaCard[data-formula-part]")].find(c=>isPartSelected(c.dataset.formulaPart));
    if(card&&window.matchMedia("(min-width:761px)").matches)card.scrollIntoView({block:"nearest",behavior:"smooth"});
  });
}
function openContextSettings({tab,title,hint,mobileOpen=true}={}){
  if(tab)setWorkspaceDockTab(tab);
  const titleEl=document.getElementById("dockContextTitle");
  const hintEl=document.getElementById("dockContextHint");
  if(titleEl&&title)titleEl.textContent=title;
  if(hintEl&&hint)hintEl.textContent=hint;
  if(mobileOpen&&window.matchMedia("(max-width:760px)").matches){
    requestAnimationFrame(()=>{
      document.getElementById("workspaceDock")?.scrollIntoView({block:"start",behavior:"smooth"});
    });
  }
}

function renderCabinet(){
  const svg=$("cabinet");
  if(!svg)return;
  const W=state.outer.W,H=state.outer.H,D=state.outer.D;
  const margin=40;
  const vw=580,vh=760;
  const scale=Math.min((vw-margin*2)/W,(vh-margin*2)/H);
  const x0=(vw-W*scale)/2,y0=(vh-H*scale)/2;
  const sx=v=>v*scale;
  const leftT=symbolThickness("左側板厚"),rightT=symbolThickness("右側板厚"),topT=symbolThickness("天板厚"),bottomT=symbolThickness("地板厚");
  const parts=[];
  parts.push(`<rect data-part-id="LEFT" x="${x0}" y="${y0+sx(leftTopInside())}" width="${sx(leftT)}" height="${sx(leftPartHeight())}" class="sideBoard${isPartSelected("LEFT")?" partSelectedSvg":""}"/>`);
  parts.push(`<rect data-part-id="RIGHT" x="${x0+sx(W-rightT)}" y="${y0+sx(rightTopInside())}" width="${sx(rightT)}" height="${sx(rightPartHeight())}" class="sideBoard${isPartSelected("RIGHT")?" partSelectedSvg":""}"/>`);
  const topX=x0+(jointAt("tl")==="side"?sx(leftT):0);
  parts.push(`<rect data-part-id="TOP" x="${topX}" y="${y0}" width="${sx(topPartWidth())}" height="${sx(topT)}" class="topBoard${isPartSelected("TOP")?" partSelectedSvg":""}"/>`);
  const bottomX=x0+(jointAt("bl")==="side"?sx(leftT):0);
  parts.push(`<rect data-part-id="BOTTOM" x="${bottomX}" y="${y0+sx(H-bottomT)}" width="${sx(bottomPartWidth())}" height="${sx(bottomT)}" class="bottomBoard${isPartSelected("BOTTOM")?" partSelectedSvg":""}"/>`);
  const content=interiorRect();
  const regions=collectRegions(state.root,content);
  regions.forEach(r=>{
    const selected=r.node.id===state.selected;
    parts.push(`<rect data-region="${r.node.id}" x="${x0+sx(r.x)}" y="${y0+sx(r.y)}" width="${sx(r.w)}" height="${sx(r.h)}" class="regionHit${selected?" selected":""}" fill="transparent"/>`);
  });
  allPartNodes(state.root).forEach(p=>{
    const owner=allRegionNodes(state.root).find(r=>r.split===p);
    if(!owner)return;
    const ownerRect=regions.find(r=>r.node===owner);
    if(!ownerRect)return;
    const geo=splitGeometry(p,ownerRect.w,ownerRect.h);
    geo.cuts.forEach(c=>{
      const cls=p.orientation==="vertical"?"dividerBoard":"shelfBoard";
      parts.push(`<rect data-part-id="${p.partId}" x="${x0+sx(ownerRect.x+c.x)}" y="${y0+sx(ownerRect.y+c.y)}" width="${sx(c.w)}" height="${sx(c.h)}" class="${cls}${isPartSelected(p.partId)?" partSelectedSvg":""}"/>`);
    });
  });
  parts.push(...renderInnerBox2D(x0,y0,scale));
  parts.push(...renderBackboards2D(x0,y0,scale,regions));
  parts.push(...renderPlinth2D(x0,y0,scale));
  parts.push(...renderLabels2D(x0,y0,scale,regions));
  svg.innerHTML=parts.join("");
  gAttachIllustrationInteractions(svg);
}

function gAttachIllustrationInteractions(g){
  g.querySelectorAll("[data-part-id]").forEach(el=>el.addEventListener("click",e=>{
    e.stopPropagation();
    setSelectedPart(el.dataset.partId);
  }));
  // v90: illustration is display-only. No region click/tap interaction.
}

function renderInnerBox2D(x0,y0,scale){
  const sx=v=>v*scale;
  const out=[];
  const content=interiorRect();
  const cfg=state.innerBox||{};
  const gap=Math.max(0,evalFormula(cfg.gapFormula||"0")||0);
  const leftOn=cfg.sides==="left"||cfg.sides==="both";
  const rightOn=cfg.sides==="right"||cfg.sides==="both";
  const topOn=cfg.top&&cfg.top!=="none";
  const bottomOn=cfg.bottom&&cfg.bottom!=="none";
  const lT=symbolThickness("左内側板厚"),rT=symbolThickness("右内側板厚"),tT=symbolThickness("内天板厚"),bT=symbolThickness("内地板厚");
  let leftInside=content.x,rightInside=content.x+content.w,topInside=content.y,bottomInside=content.y+content.h;
  if(leftOn){const x=content.x+gap;out.push(`<rect data-part-id="INNER_LEFT" x="${x0+sx(x)}" y="${y0+sx(content.y+(topOn&&cfg.top==="outer"?tT:0))}" width="${sx(lT)}" height="${sx(content.h-(topOn&&cfg.top==="outer"?tT:0)-(bottomOn&&cfg.bottom==="outer"?bT:0))}" class="innerBoard${isPartSelected("INNER_LEFT")?" partSelectedSvg":""}"/>`);leftInside=x+lT}
  if(rightOn){const x=content.x+content.w-gap-rT;out.push(`<rect data-part-id="INNER_RIGHT" x="${x0+sx(x)}" y="${y0+sx(content.y+(topOn&&cfg.top==="outer"?tT:0))}" width="${sx(rT)}" height="${sx(content.h-(topOn&&cfg.top==="outer"?tT:0)-(bottomOn&&cfg.bottom==="outer"?bT:0))}" class="innerBoard${isPartSelected("INNER_RIGHT")?" partSelectedSvg":""}"/>`);rightInside=x}
  if(topOn){const x=cfg.top==="outer"?content.x:leftInside;const w=cfg.top==="outer"?content.w:rightInside-leftInside;out.push(`<rect data-part-id="INNER_TOP" x="${x0+sx(x)}" y="${y0+sx(content.y)}" width="${sx(w)}" height="${sx(tT)}" class="innerBoard${isPartSelected("INNER_TOP")?" partSelectedSvg":""}"/>`);topInside=content.y+tT}
  if(bottomOn){const x=cfg.bottom==="outer"?content.x:leftInside;const w=cfg.bottom==="outer"?content.w:rightInside-leftInside;out.push(`<rect data-part-id="INNER_BOTTOM" x="${x0+sx(x)}" y="${y0+sx(content.y+content.h-bT)}" width="${sx(w)}" height="${sx(bT)}" class="innerBoard${isPartSelected("INNER_BOTTOM")?" partSelectedSvg":""}"/>`);bottomInside=content.y+content.h-bT}
  return out;
}

function renderBackboards2D(x0,y0,scale,regions){
  const sx=v=>v*scale;
  const out=[];
  if(state.backboard.enabled){
    const c=interiorRect();
    const x=state.backboard.mode==="outside"?0:c.x;
    const y=state.backboard.mode==="outside"?0:c.y;
    const w=state.backboard.mode==="outside"?state.outer.W:c.w;
    const h=state.backboard.mode==="outside"?state.outer.H:c.h;
    out.push(`<rect data-part-id="BACKBOARD" x="${x0+sx(x)}" y="${y0+sx(y)}" width="${sx(w)}" height="${sx(h)}" class="backboardGhost${isPartSelected("BACKBOARD")?" partSelectedSvg":""}"/>`);
  }
  regions.forEach(r=>{
    if(!r.node.innerBackboard)return;
    out.push(`<rect data-part-id="${r.node.innerBackboard.partId}" x="${x0+sx(r.x)}" y="${y0+sx(r.y)}" width="${sx(r.w)}" height="${sx(r.h)}" class="innerBackGhost${isPartSelected(r.node.innerBackboard.partId)?" partSelectedSvg":""}"/>`);
  });
  return out;
}

function renderPlinth2D(x0,y0,scale){
  if(!state.plinth.enabled)return[];
  const sx=v=>v*scale;
  const h=Math.max(1,evalFormula(state.plinth.heightFormula)||60);
  const out=[];
  if(state.plinth.front)out.push(`<rect data-part-id="PLINTH_FRONT" x="${x0}" y="${y0+sx(state.outer.H-h)}" width="${sx(state.outer.W)}" height="${sx(h)}" class="plinthBoard${isPartSelected("PLINTH_FRONT")?" partSelectedSvg":""}"/>`);
  return out;
}

function renderLabels2D(x0,y0,scale,regions){
  const sx=v=>v*scale;
  const out=[];
  const W=state.outer.W,H=state.outer.H;
  out.push(`<text x="${x0+sx(W/2)}" y="${y0-12}" class="dimLabel" text-anchor="middle">W ${mm(W)}</text>`);
  out.push(`<text x="${x0-16}" y="${y0+sx(H/2)}" class="dimLabel" text-anchor="middle" transform="rotate(-90 ${x0-16} ${y0+sx(H/2)})">H ${mm(H)}</text>`);
  out.push(`<text x="${x0+sx(symbolThickness("左側板厚")/2)}" y="${y0+sx(H/2)}" class="boardLabel" text-anchor="middle" transform="rotate(-90 ${x0+sx(symbolThickness("左側板厚")/2)} ${y0+sx(H/2)})">左側板</text>`);
  out.push(`<text x="${x0+sx(W-symbolThickness("右側板厚")/2)}" y="${y0+sx(H/2)}" class="boardLabel" text-anchor="middle" transform="rotate(90 ${x0+sx(W-symbolThickness("右側板厚")/2)} ${y0+sx(H/2)})">右側板</text>`);
  regions.forEach(r=>{
    out.push(`<text x="${x0+sx(r.x+r.w/2)}" y="${y0+sx(r.y+r.h/2)}" class="regionLabel" text-anchor="middle">${r.node.id}</text>`);
  });
  return out;
}

function draw3D(){
  const canvas=$("threeCanvas");
  if(!canvas)return;
  const ctx=canvas.getContext("2d");
  const rect=canvas.getBoundingClientRect();
  const dpr=Math.min(window.devicePixelRatio||1,2);
  canvas.width=Math.max(1,Math.floor(rect.width*dpr));
  canvas.height=Math.max(1,Math.floor(rect.height*dpr));
  ctx.setTransform(dpr,0,0,dpr,0,0);
  const w=rect.width,h=rect.height;
  ctx.clearRect(0,0,w,h);
  ctx.save();
  ctx.translate(w/2,h/2);
  const scale=Math.min(w/(state.outer.W*1.65),h/(state.outer.H*1.65));
  const yaw=threeAngles().yaw,pitch=threeAngles().pitch;
  const parts=build3DParts();
  parts.sort((a,b)=>project3D(a.cx,a.cy,a.cz,yaw,pitch).z-project3D(b.cx,b.cy,b.cz,yaw,pitch).z);
  parts.forEach(p=>drawBox3D(ctx,p,scale,yaw,pitch));
  ctx.restore();
}

function threeAngles(){
  if(state.threeView==="front")return{yaw:0,pitch:-0.04};
  if(state.threeView==="back")return{yaw:Math.PI,pitch:-0.04};
  if(state.threeView==="leftFront")return{yaw:-0.62,pitch:-0.22};
  return{yaw:0.62,pitch:-0.22};
}

function project3D(x,y,z,yaw,pitch){
  const cy=Math.cos(yaw),sy=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);
  const xx=x*cy+z*sy;
  const zz=-x*sy+z*cy;
  const yy=y*cp-zz*sp;
  const z2=y*sp+zz*cp;
  return{x:-xx,y:yy,z:z2};
}

function build3DParts(){
  const W=state.outer.W,H=state.outer.H,D=state.outer.D;
  const bodyD=state.backboard.enabled&&state.backboard.mode==="outside"?Math.max(1,D-symbolThickness("背板厚")):D;
  const lT=symbolThickness("左側板厚"),rT=symbolThickness("右側板厚"),tT=symbolThickness("天板厚"),bT=symbolThickness("地板厚");
  const arr=[];
  arr.push({id:"LEFT",type:"side",cx:lT/2,cy:H/2,cz:bodyD/2,w:lT,h:H,d:bodyD});
  arr.push({id:"RIGHT",type:"side",cx:W-rT/2,cy:H/2,cz:bodyD/2,w:rT,h:H,d:bodyD});
  arr.push({id:"TOP",type:"top",cx:W/2,cy:tT/2,cz:bodyD/2,w:W,h:tT,d:bodyD});
  arr.push({id:"BOTTOM",type:"bottom",cx:W/2,cy:H-bT/2,cz:bodyD/2,w:W,h:bT,d:bodyD});
  const content=interiorRect();
  const regions=collectRegions(state.root,content);
  allPartNodes(state.root).forEach(p=>{
    const owner=allRegionNodes(state.root).find(r=>r.split===p);
    const ownerRect=regions.find(r=>r.node===owner);
    if(!ownerRect)return;
    const geo=splitGeometry(p,ownerRect.w,ownerRect.h);
    geo.cuts.forEach(c=>{
      arr.push({id:p.partId,type:p.orientation==="vertical"?"divider":"shelf",cx:ownerRect.x+c.x+c.w/2,cy:ownerRect.y+c.y+c.h/2,cz:bodyD/2,w:c.w,h:c.h,d:bodyD});
    });
  });
  innerBoxParts().forEach(p=>{
    if(p.id==="INNER_TOP")arr.push({id:p.id,type:"innerTop",cx:W/2,cy:tT+p.thickness/2,cz:bodyD/2,w:p.w,h:p.thickness,d:bodyD});
    if(p.id==="INNER_BOTTOM")arr.push({id:p.id,type:"innerBottom",cx:W/2,cy:H-bT-p.thickness/2,cz:bodyD/2,w:p.w,h:p.thickness,d:bodyD});
    if(p.id==="INNER_LEFT")arr.push({id:p.id,type:"innerSide",cx:lT+(evalFormula(state.innerBox.gapFormula)||0)+p.thickness/2,cy:H/2,cz:bodyD/2,w:p.thickness,h:p.w,d:bodyD});
    if(p.id==="INNER_RIGHT")arr.push({id:p.id,type:"innerSide",cx:W-rT-(evalFormula(state.innerBox.gapFormula)||0)-p.thickness/2,cy:H/2,cz:bodyD/2,w:p.thickness,h:p.w,d:bodyD});
  });
  if(state.backboard.enabled){
    const bt=symbolThickness("背板厚");
    const z=state.backboard.mode==="outside"?D-bt/2:Math.max(bt/2,bodyD-bt/2);
    arr.push({id:"BACKBOARD",type:"backboard",cx:W/2,cy:H/2,cz:z,w:state.backboard.mode==="outside"?W:content.w,h:state.backboard.mode==="outside"?H:content.h,d:bt});
  }
  regions.forEach(r=>{
    if(!r.node.innerBackboard)return;
    const ib=r.node.innerBackboard;
    const bt=partThickness(ib.partId,4);
    const off=Math.max(0,evalFormula(ib.formula||"50")||50);
    const z=ib.ref==="front"?off+bt/2:Math.max(bt/2,bodyD-off-bt/2);
    arr.push({id:ib.partId,type:"innerBackboard",cx:r.x+r.w/2,cy:r.y+r.h/2,cz:z,w:r.w,h:r.h,d:bt});
  });
  if(state.plinth.enabled){
    const ph=Math.max(1,evalFormula(state.plinth.heightFormula)||60);
    if(state.plinth.front)arr.push({id:"PLINTH_FRONT",type:"plinth",cx:W/2,cy:H-ph/2,cz:partThickness("PLINTH_FRONT",18)/2,w:W,h:ph,d:partThickness("PLINTH_FRONT",18)});
  }
  return arr;
}

function drawBox3D(ctx,p,scale,yaw,pitch){
  const x=p.cx-state.outer.W/2,y=p.cy-state.outer.H/2,z=p.cz-state.outer.D/2;
  const hw=p.w/2,hh=p.h/2,hd=p.d/2;
  const verts=[];
  for(const dx of[-hw,hw])for(const dy of[-hh,hh])for(const dz of[-hd,hd])verts.push(project3D(x+dx,y+dy,z+dz,yaw,pitch));
  const pts=verts.map(v=>({x:v.x*scale,y:v.y*scale,z:v.z}));
  const faces=[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]];
  faces.sort((a,b)=>a.reduce((s,i)=>s+pts[i].z,0)-b.reduce((s,i)=>s+pts[i].z,0));
  faces.forEach(f=>{
    const a=pts[f[0]],b=pts[f[1]],c=pts[f[2]];
    const cross=(b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x);
    if(cross<=0)return;
    ctx.beginPath();ctx.moveTo(pts[f[0]].x,pts[f[0]].y);f.slice(1).forEach(i=>ctx.lineTo(pts[i].x,pts[i].y));ctx.closePath();
    ctx.fillStyle=isPartSelected(p.id)?"rgba(199,120,61,.34)":"rgba(215,205,192,.74)";
    ctx.strokeStyle=isPartSelected(p.id)?"#A85F32":"#7d746a";
    ctx.lineWidth=isPartSelected(p.id)?1.7:0.8;ctx.fill();ctx.stroke();
  });
}

function renderHistoryEditor(){
  const editor=$("historyEditor");
  if(!editor)return;
  const rows=formulas();
  const id=state.historySelection&&rows.some(r=>r.id===state.historySelection)?state.historySelection:rows[0]?.id;
  if(!id){editor.innerHTML="";return}
  state.historySelection=id;
  const r=rows.find(x=>x.id===id);
  const regionMap=buildCutRegionMap(rows);
  const s1=resolveCutFormula(r.f1,rows,regionMap),s2=resolveCutFormula(r.f2,rows,regionMap);
  const compOptions=state.compositions.map(c=>`<option value="${c.id}"${partCompositionId(id)===c.id?" selected":""}>${escapeHtml(c.name)}</option>`).join("");
  editor.innerHTML=`<div class="historyEditorCard">
    <div class="historyEditorHead"><strong>${escapeHtml(partDisplayName(id))}</strong><span>${Number.isFinite(s1)?mm(s1):"計算未確定"} × ${Number.isFinite(s2)?mm(s2):"計算未確定"}</span></div>
    <label>名称<input id="historyGenericPartName" value="${escapeAttr(partDisplayName(id))}"></label>
    <label>式①<input id="historyF1" value="${escapeAttr(r.f1)}"></label>
    <label>式②<input id="historyF2" value="${escapeAttr(r.f2)}"></label>
    <label>材料構成<select id="historyComposition">${compOptions}</select></label>
    <label>木目<select id="historyGrain"><option value="none"${(state.partGrain[id]||"none")==="none"?" selected":""}>なし</option><option value="long"${state.partGrain[id]==="long"?" selected":""}>長手</option><option value="short"${state.partGrain[id]==="short"?" selected":""}>短手</option></select></label>
    ${r.kind==="custom"?`<label>数量<input id="historyCustomQty" type="number" min="1" value="${Math.max(1,safeNumber(r.qty,1))}"></label><button id="historyDeletePart" class="ghost danger">この追加部材を削除</button>`:""}
  </div>`;
  $("historyGenericPartName").addEventListener("change",e=>{
    const value=e.target.value.trim();
    state.partNames[id]=value;
    const cp=state.customParts.find(p=>p.id===id);if(cp)cp.name=value;
    renderFormulaList();
  });
  $("historyF1").addEventListener("change",e=>setPartFormulaOverride(id,"f1",e.target.value));
  $("historyF2").addEventListener("change",e=>setPartFormulaOverride(id,"f2",e.target.value));
  $("historyComposition").addEventListener("change",e=>{state.partComposition[id]=e.target.value;update()});
  $("historyGrain").addEventListener("change",e=>{state.partGrain[id]=e.target.value;renderFormulaList()});
  $("historyCustomQty")?.addEventListener("change",e=>{const cp=state.customParts.find(p=>p.id===id);if(cp){cp.qty=Math.max(1,parseInt(e.target.value||"1",10)||1);renderFormulaList()}});
  $("historyDeletePart")?.addEventListener("click",()=>{state.customParts=state.customParts.filter(p=>p.id!==id);delete state.partNames[id];delete state.partComposition[id];delete state.partGrain[id];state.historySelection="";renderFormulaList()});
}

function setPartFormulaOverride(id,key,value){
  const cp=state.customParts.find(p=>p.id===id);
  if(cp){cp[key]=value;renderFormulaList();return}
  state.overrides[id]??={};
  state.overrides[id][key]=value;
  renderFormulaList();
}

function escapeHtml(s){return String(s??"").replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]))}
function escapeAttr(s){return escapeHtml(s).replace(/"/g,"&quot;")}

function renderInnerBackControls(){
  const r=selectedRegion();
  const has=!!r?.innerBackboard;
  const toggle=$("innerBackToggle");
  const fields=$("innerBackFields");
  if(!toggle||!fields)return;
  toggle.textContent=has?"内背板あり":"＋ 内背板";
  toggle.classList.toggle("on",has);
  fields.classList.toggle("hidden",!has);
  if(has){
    $("innerBackRef").querySelectorAll("button").forEach(b=>b.classList.toggle("active",b.dataset.value===r.innerBackboard.ref));
    $("innerBackFormula").value=r.innerBackboard.formula||"50";
    $("innerBackStatus").textContent=`${r.id} / ${r.innerBackboard.ref==="front"?"前":"後"}から ${r.innerBackboard.formula||"50"}`;
  }
}

function toggleInnerBack(){
  const r=selectedRegion();
  if(!r)return;
  if(r.innerBackboard)r.innerBackboard=null;
  else r.innerBackboard={partId:`INNER_BACK_${r.id}`,ref:"back",formula:"50"};
  update();
}

function renderPlinthControls(){
  const p=state.plinth;
  $("plinthToggle").textContent=p.enabled?"あり":"なし";
  $("plinthToggle").classList.toggle("on",p.enabled);
  $("plinthFields").classList.toggle("hidden",!p.enabled);
  $("plinthHeight").value=p.heightFormula;
  $("plinthFrontSetback").value=p.frontSetbackFormula;
  $("plinthSideSetback").value=p.sideSetbackFormula;
  $("plinthBackSetback").value=p.backSetbackFormula;
  $("plinthSideDepth").value=p.sideDepthFormula;
  document.querySelectorAll("[data-plinth-edge]").forEach(b=>b.classList.toggle("on",!!p[b.dataset.plinthEdge]));
  $("plinthSideDrop").querySelectorAll("button").forEach(b=>b.classList.toggle("active",b.dataset.value===(p.sideDrop.left==="plinth"?"plinth":"body")));
}

function renderBackboardControls(){
  const b=state.backboard;
  $("backboardToggle").textContent=b.enabled?"あり":"なし";
  $("backboardToggle").classList.toggle("on",b.enabled);
  $("backboardFields").classList.toggle("hidden",!b.enabled);
  $("backboardMode").querySelectorAll("button").forEach(btn=>btn.classList.toggle("active",btn.dataset.value===b.mode));
  $("backboardModeNote").textContent=b.mode==="outside"?"外寸Dは固定。箱本体の奥行を D - 背板厚 にします。":b.mode==="inset5"?"四周から5mm内側に入る背板":"箱の内側に収まるサイズ";
}

function renderInnerBoxControls(){
  const c=state.innerBox;
  document.querySelectorAll("[data-inner-box-top] button").forEach(b=>b.classList.toggle("active",b.dataset.mode===c.top));
  document.querySelectorAll("[data-inner-box-sides] button").forEach(b=>b.classList.toggle("active",b.dataset.mode===c.sides));
  document.querySelectorAll("[data-inner-box-bottom] button").forEach(b=>b.classList.toggle("active",b.dataset.mode===c.bottom));
  $("innerTopStateLabel").textContent=c.top==="none"?"なし":c.top==="outer"?"側板内":"内側板間";
  $("innerSidesStateLabel").textContent=c.sides==="none"?"なし":c.sides==="both"?"両側":c.sides==="left"?"左":"右";
  $("innerBottomStateLabel").textContent=c.bottom==="none"?"なし":c.bottom==="outer"?"側板内":"内側板間";
  $("innerBoxGap").value=c.gapFormula||"0";
}

function renderRegionControls(){
  const r=selectedRegion();
  $("selectedInfo").textContent=r?.id||"外箱";
  $("placeMode").querySelectorAll("button").forEach(b=>b.classList.toggle("active",b.dataset.value===state.placeMode));
  $("horizontalAxisRef").querySelectorAll("button").forEach(b=>b.classList.toggle("active",b.dataset.value===state.horizontalRef));
  $("verticalAxisRef").querySelectorAll("button").forEach(b=>b.classList.toggle("active",b.dataset.value===state.verticalRef));
  $("placeDetail").classList.toggle("hidden",state.placeMode==="equal");
  $("placeFormula").value=state.placeFormula;
  $("undoSplit").disabled=!(r?.split||findParent(state.root,state.selected)?.split);
}

function update(){
  state.outer.W=resolveOuterDimension("W",state.outerFormula)||state.outer.W;
  state.outer.H=resolveOuterDimension("H",state.outerFormula)||state.outer.H;
  state.outer.D=resolveOuterDimension("D",state.outerFormula)||state.outer.D;
  $("outerW").value=state.outerFormula.W;
  $("outerH").value=state.outerFormula.H;
  $("outerD").value=state.outerFormula.D;
  renderCabinet();
  renderFormulaList();
  renderInnerBoxControls();
  renderRegionControls();
  renderInnerBackControls();
  renderPlinthControls();
  renderBackboardControls();
  renderProjectMeta();
  draw3D();
}

function resolveOuterDimension(axis,formulas,stack=[]){
  if(stack.includes(axis))return NaN;
  let src=normalizeExpression(formulas?.[axis]??state.outerFormula?.[axis]??state.outer?.[axis]);
  if(!src)return NaN;
  src=src.replace(/\b([WHD])\b/g,(m,a)=>{
    if(a===axis||stack.includes(a))return "NaN";
    const v=resolveOuterDimension(a,formulas,[...stack,axis]);
    return Number.isFinite(v)?String(v):"NaN";
  });
  if(src.includes("NaN")||!/^[0-9+\-*/().]+$/.test(src))return NaN;
  try{const n=Function(`"use strict";return (${src})`)();return Number.isFinite(n)&&n>0?n:NaN}catch{return NaN}
}

function renderProjectMeta(){
  $("patternName").value=state.unitName;
  $("mobileThreeUnitName").textContent=state.unitName;
  $("mobileThreeDimensions").textContent=`W ${mm(state.outer.W)} · H ${mm(state.outer.H)} · D ${mm(state.outer.D)}`;
  $("mobileThreeProjectName").textContent=currentProjectName||"案件未設定";
}

function snapshotUnit(){
  readOuter();
  if(!currentUnitId)currentUnitId=makeUnitId();
  return{
    version:91,
    id:currentUnitId,
    savedAt:new Date().toISOString(),
    name:$("patternName").value.trim()||"ユニット 01",
    outer:{...state.outer},outerFormula:{...state.outerFormula},
    joints:{...state.joints},root:structuredClone(state.root),nextRegion:state.nextRegion,nextPart:state.nextPart,nextHistory:state.nextHistory,
    plinth:structuredClone(state.plinth),backboard:structuredClone(state.backboard),innerBox:structuredClone(state.innerBox),
    materials:structuredClone(state.materials),compositions:structuredClone(state.compositions),defaultCompositionId:state.defaultCompositionId,
    partComposition:{...state.partComposition},partNames:{...state.partNames},partGrain:{...state.partGrain},overrides:structuredClone(state.overrides),
    customParts:structuredClone(state.customParts),nextCustomPart:state.nextCustomPart,
    placeMode:state.placeMode,horizontalRef:state.horizontalRef,verticalRef:state.verticalRef,placeFormula:state.placeFormula,
    regionContents:structuredClone(state.regionContents||{}),
  };
}

function applyUnit(data){
  if(!data)return;
  currentUnitId=data.id||makeUnitId();
  state.unitName=data.name||"ユニット 01";
  state.outer={...state.outer,...(data.outer||{})};
  state.outerFormula={W:String(data.outerFormula?.W??data.outer?.W??state.outer.W),H:String(data.outerFormula?.H??data.outer?.H??state.outer.H),D:String(data.outerFormula?.D??data.outer?.D??state.outer.D)};
  state.joints={...state.joints,...(data.joints||{})};
  state.root=structuredClone(data.root||{id:"R1",split:null,innerBackboard:null});
  state.nextRegion=data.nextRegion||2;state.nextPart=data.nextPart||1;state.nextHistory=data.nextHistory||1;
  state.plinth={...state.plinth,...(data.plinth||{}),sideDrop:{...state.plinth.sideDrop,...(data.plinth?.sideDrop||{})}};
  state.backboard={...state.backboard,...(data.backboard||{})};
  state.innerBox={...state.innerBox,...(data.innerBox||{})};
  state.materials=structuredClone(data.materials||state.materials);state.compositions=structuredClone(data.compositions||state.compositions);
  state.defaultCompositionId=data.defaultCompositionId||state.defaultCompositionId;
  state.partComposition={...(data.partComposition||{})};state.partNames={...(data.partNames||{})};state.partGrain={...(data.partGrain||{})};state.overrides=structuredClone(data.overrides||{});
  state.customParts=structuredClone(data.customParts||[]);state.nextCustomPart=data.nextCustomPart||1;
  state.placeMode=data.placeMode||"equal";state.horizontalRef=data.horizontalRef||"left";state.verticalRef=data.verticalRef||"top";state.placeFormula=data.placeFormula||"600";
  state.regionContents=structuredClone(data.regionContents||{});
  state.selected="R1";state.historySelection="";state.selectedPartId=null;
  update();
}

const PROJECT_STORE_KEY="maProjectsV31";
let currentProjectId=null,currentProjectName="",currentUnitId=null;
function makeProjectId(){return `PRJ_${Date.now()}_${Math.random().toString(36).slice(2,7)}`}
function makeUnitId(){return `UNT_${Date.now()}_${Math.random().toString(36).slice(2,7)}`}
function loadProjects(){try{return JSON.parse(localStorage.getItem(PROJECT_STORE_KEY)||"[]")}catch{return[]}}
function saveProjects(p){localStorage.setItem(PROJECT_STORE_KEY,JSON.stringify(p))}
function currentProject(){return loadProjects().find(p=>p.id===currentProjectId)||null}
function currentUnit(){return currentProject()?.units?.find(u=>u.id===currentUnitId)||null}

function createProject(name){
  const projects=loadProjects();const p={id:makeProjectId(),name:name.trim()||"案件",units:[],createdAt:new Date().toISOString(),updatedAt:new Date().toISOString()};
  projects.unshift(p);saveProjects(projects);openProject(p.id);
}
function openProject(id){
  const p=loadProjects().find(x=>x.id===id);if(!p)return;
  currentProjectId=p.id;currentProjectName=p.name;currentUnitId=null;showProjectView();renderProjectUnits();
}
function saveCurrentUnit(){
  if(!currentProjectId)return;
  const projects=loadProjects();const p=projects.find(x=>x.id===currentProjectId);if(!p)return;
  const snap=snapshotUnit();state.unitName=snap.name;
  const i=p.units.findIndex(u=>u.id===snap.id);if(i>=0)p.units[i]=snap;else p.units.push(snap);
  p.updatedAt=new Date().toISOString();saveProjects(projects);renderProjectMeta();
}
function createNewUnit(){
  currentUnitId=makeUnitId();resetState();state.unitName=`ユニット ${String((currentProject()?.units?.length||0)+1).padStart(2,"0")}`;showEditor();update();
}
function openUnit(id){const u=currentProject()?.units?.find(x=>x.id===id);if(!u)return;applyUnit(u);showEditor()}

function resetState(){
  state.outer={W:1800,H:900,D:450};state.outerFormula={W:"1800",H:"900",D:"450"};state.joints={tl:"side",tr:"side",bl:"side",br:"side"};
  state.root={id:"R1",split:null,innerBackboard:null};state.selected="R1";state.nextRegion=2;state.nextPart=1;state.nextHistory=1;state.historySelection="";state.selectedPartId=null;
  state.plinth={enabled:false,heightFormula:"60",front:true,left:true,right:true,back:false,frontSetbackFormula:"50",sideSetbackFormula:"0",backSetbackFormula:"0",sideDepthFormula:"100",sideDrop:{left:"body",right:"body"}};
  state.backboard={enabled:true,mode:"inside"};state.innerBox={top:"none",sides:"none",bottom:"none",gapFormula:"0"};state.partComposition={};state.partNames={};state.partGrain={};state.overrides={};state.customParts=[];state.nextCustomPart=1;state.regionContents={};
  state.placeMode="equal";state.horizontalRef="left";state.verticalRef="top";state.placeFormula="600";
}

function showHome(){document.body.className="page-home";$("homeView").classList.remove("hidden");$("projectView").classList.add("hidden");$("editorView").classList.add("hidden");renderHomeProjects()}
function showProjectView(){document.body.className="page-project";$("homeView").classList.add("hidden");$("projectView").classList.remove("hidden");$("editorView").classList.add("hidden");$("projectTitle").textContent=currentProjectName}
function showEditor(){document.body.className="mobileStructurePreview";$("homeView").classList.add("hidden");$("projectView").classList.add("hidden");$("editorView").classList.remove("hidden");update()}

function renderHomeProjects(){
  const host=$("homeProjects");const ps=loadProjects();
  host.innerHTML=ps.length?ps.map(p=>`<button class="projectCard" data-project-open="${p.id}"><strong>${escapeHtml(p.name)}</strong><span>${p.units?.length||0} units</span></button>`).join(""):`<div class="emptyCard">案件を作成してください。</div>`;
  host.querySelectorAll("[data-project-open]").forEach(b=>b.addEventListener("click",()=>openProject(b.dataset.projectOpen)));
}
function renderProjectUnits(){
  const p=currentProject();if(!p)return;$("projectTitle").textContent=p.name;
  const host=$("projectUnits");host.innerHTML=(p.units||[]).map(u=>`<button class="unitCard" data-unit-open="${u.id}"><strong>${escapeHtml(u.name)}</strong><span>W ${u.outer?.W||"-"} · H ${u.outer?.H||"-"} · D ${u.outer?.D||"-"}</span></button>`).join("")||`<div class="emptyCard">ユニットはまだありません。</div>`;
  host.querySelectorAll("[data-unit-open]").forEach(b=>b.addEventListener("click",()=>openUnit(b.dataset.unitOpen)));
}

function setupEvents(){
  $("newProjectBtn").addEventListener("click",()=>$("newProjectDialog").showModal());
  $("cancelNewProject").addEventListener("click",()=>$("newProjectDialog").close());
  $("createProject").addEventListener("click",()=>{createProject($("newProjectName").value);$("newProjectDialog").close();$("newProjectName").value=""});
  $("projectBackHome").addEventListener("click",showHome);$("projectNewUnit").addEventListener("click",createNewUnit);
  $("editorBackProject").addEventListener("click",()=>{saveCurrentUnit();showProjectView();renderProjectUnits()});
  $("saveUnitBtn").addEventListener("click",saveCurrentUnit);
  $("patternName").addEventListener("change",e=>{state.unitName=e.target.value;renderProjectMeta()});
  ["W","H","D"].forEach(a=>$("outer"+a).addEventListener("change",e=>{state.outerFormula[a]=e.target.value;update()}));
  $("countMinus").addEventListener("click",()=>$("addCount").value=Math.max(1,(parseInt($("addCount").value||"1",10)||1)-1));
  $("countPlus").addEventListener("click",()=>$("addCount").value=(parseInt($("addCount").value||"1",10)||1)+1);
  $("addDivider").addEventListener("click",()=>splitSelected("vertical"));$("addShelf").addEventListener("click",()=>splitSelected("horizontal"));$("undoSplit").addEventListener("click",undoSelectedSplit);
  $("placeMode").querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>{state.placeMode=b.dataset.value;renderRegionControls()}));
  $("horizontalAxisRef").querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>{state.horizontalRef=b.dataset.value;renderRegionControls()}));
  $("verticalAxisRef").querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>{state.verticalRef=b.dataset.value;renderRegionControls()}));
  $("placeFormula").addEventListener("change",e=>{state.placeFormula=e.target.value;update()});
  $("innerBackToggle").addEventListener("click",toggleInnerBack);
  $("innerBackRef").querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>{const r=selectedRegion();if(r?.innerBackboard){r.innerBackboard.ref=b.dataset.value;update()}}));
  $("innerBackFormula").addEventListener("change",e=>{const r=selectedRegion();if(r?.innerBackboard){r.innerBackboard.formula=e.target.value;update()}});
  $("plinthToggle").addEventListener("click",()=>{state.plinth.enabled=!state.plinth.enabled;update()});
  document.querySelectorAll("[data-plinth-edge]").forEach(b=>b.addEventListener("click",()=>{state.plinth[b.dataset.plinthEdge]=!state.plinth[b.dataset.plinthEdge];update()}));
  ["Height","FrontSetback","SideSetback","BackSetback","SideDepth"].forEach(k=>$("plinth"+k).addEventListener("change",e=>{const map={Height:"heightFormula",FrontSetback:"frontSetbackFormula",SideSetback:"sideSetbackFormula",BackSetback:"backSetbackFormula",SideDepth:"sideDepthFormula"};state.plinth[map[k]]=e.target.value;update()}));
  $("plinthSideDrop").querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>{state.plinth.sideDrop.left=b.dataset.value;state.plinth.sideDrop.right=b.dataset.value;update()}));
  $("backboardToggle").addEventListener("click",()=>{state.backboard.enabled=!state.backboard.enabled;update()});
  $("backboardMode").querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>{state.backboard.mode=b.dataset.value;update()}));
  document.querySelectorAll("[data-inner-box-top] button").forEach(b=>b.addEventListener("click",()=>{state.innerBox.top=b.dataset.mode;update()}));
  document.querySelectorAll("[data-inner-box-sides] button").forEach(b=>b.addEventListener("click",()=>{state.innerBox.sides=b.dataset.mode;update()}));
  document.querySelectorAll("[data-inner-box-bottom] button").forEach(b=>b.addEventListener("click",()=>{state.innerBox.bottom=b.dataset.mode;update()}));
  $("innerBoxGap").addEventListener("change",e=>{state.innerBox.gapFormula=e.target.value;update()});
  $("addCustomPart").addEventListener("click",()=>{const id=`EXTRA_${state.nextCustomPart++}`;state.customParts.push({id,name:"追加部材",f1:"W",f2:"D",qty:1,kind:"custom"});state.historySelection=id;renderFormulaList()});
}

function initWorkspaceDock(){
  const dock=$("workspaceDock");if(!dock)return;
  dock.querySelectorAll("[data-workspace-dock-tab]").forEach(btn=>btn.addEventListener("click",()=>setWorkspaceDockTab(btn.dataset.workspaceDockTab)));
}
function setWorkspaceDockTab(tab){
  if(!["box","region","joint","plinth","backboard"].includes(tab))return;
  workspaceDockState.tab=tab;
  document.querySelectorAll("[data-workspace-dock-tab]").forEach(b=>b.classList.toggle("active",b.dataset.workspaceDockTab===tab));
  document.querySelectorAll("[data-workspace-dock-panel]").forEach(p=>p.classList.toggle("active",p.dataset.workspaceDockPanel===tab));
  const labels={box:["箱の構成","内天板・内側板・内地板を設定します。"],region:["棚・束","選択中の区画に棚・束を追加・配置します。"],joint:["四隅","四隅の勝ち負けを1か所ずつ確認します。"],plinth:["巾木","巾木の有無・位置・寸法を編集します。"],backboard:["背板","背板の納まりを編集します。"]};
  if(!state.selectedPartId){
    const v=labels[tab],title=$("dockContextTitle"),hint=$("dockContextHint");
    if(title&&v)title.textContent=v[0];if(hint&&v)hint.textContent=v[1];
  }
  saveWorkspaceDockState();
}
function saveWorkspaceDockState(){try{localStorage.setItem(WORKSPACE_DOCK_KEY,JSON.stringify(workspaceDockState))}catch{}}
function loadWorkspaceDockState(){try{Object.assign(workspaceDockState,JSON.parse(localStorage.getItem(WORKSPACE_DOCK_KEY)||"{}"))}catch{}}

setupEvents();initWorkspaceDock();loadWorkspaceDockState();setWorkspaceDockTab(workspaceDockState.tab||"box");showHome();
</script>
</body>
</html>
