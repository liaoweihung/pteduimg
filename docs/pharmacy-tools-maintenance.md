# 藥局工具與 Hub 維護規範

新增、修改、更名、移動、退出或移除藥局工作工具時，操作前讀完本檔。醫藥計算器及含計算或判讀邏輯的工具，另依 [醫藥計算器工作規範 v1.0](medical-calculator-guide-v1.md) 處理醫療來源、交接包、驗證與手機版面。所有本機路徑以 pteduimg 根目錄為準；Hub 的實際 checkout 仍須另外核對。技術與 Git 規範見 [建置與發布](site-build-and-release.md)，管理紀錄見 [專案管理 SOP](project-management/README.md)。

## Pharmacy Tool Pages and Hub Synchronization

Whenever adding, modifying, renaming, moving, retiring, or removing a pharmacy work tool page, check the corresponding hub pages as part of the same task and update them when needed.

- The tool directory is a separate page: `https://liaoweihung.github.io/hub/pharmacy-tools.html`.
- `https://liaoweihung.github.io/hub/index.html` contains only the directory entry. Keep `藥局工作用工具` as the last entry, immediately after `藥師自我學資料分享`; do not embed the tool list in the hub homepage.
- Tool implementations and their assets may remain in `/pteduimg/`. Hub tool links must point to their correct published URLs, including any nested paths such as `/pteduimg/web/`.
- For new public pharmacy work tools, add an entry to `hub/pharmacy-tools.html`. For existing tools, check the displayed name, description, URL, ordering, and availability; update affected entries and any displayed tool count. Do not automatically list unpublished prototypes or hidden tools.
- Tool return links, including links rendered by shared JavaScript shells, should lead to `https://liaoweihung.github.io/hub/pharmacy-tools.html`. Check the directory link in `pteduimg/calc.html` as well.
- Verify the hub homepage entry, the complete tool directory, tool destinations, and return navigation. If a tool change does not require a hub edit, explicitly report that the hub was checked and remains consistent.
- `hub` and `pteduimg` are separate Git repositories. Locate the hub checkout and verify its remote is `https://github.com/liaoweihung/hub.git` before editing. A checkout may exist at `output/hub/`, but this is a local working location, not the published URL. Never stage the nested hub repository as part of a pteduimg commit.
- If hub source is unavailable, obtain the repository or report the missing synchronization work; do not silently mark the task complete. When publishing is requested, commit/push each affected repository separately and identify both results. Publish a new hub directory page before links that depend on it.
- Changes to tool navigation must preserve the existing cache-first strategy and user-initiated update experience. Run `python scripts/check_site.py` after changes to tool navigation or shared tool shells.
