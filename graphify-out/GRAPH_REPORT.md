# Graph Report - .  (2026-04-18)

## Corpus Check
- 11 files · ~82,845 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 92 nodes · 144 edges · 11 communities detected
- Extraction: 89% EXTRACTED · 10% INFERRED · 1% AMBIGUOUS · INFERRED: 15 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Core Flask Routes|Core Flask Routes]]
- [[_COMMUNITY_User Study Materials|User Study Materials]]
- [[_COMMUNITY_Gemini Study AI|Gemini Study AI]]
- [[_COMMUNITY_Moonlit Landscape Image|Moonlit Landscape Image]]
- [[_COMMUNITY_Linux Launcher Setup|Linux Launcher Setup]]
- [[_COMMUNITY_Java Mac Compatibility|Java Mac Compatibility]]
- [[_COMMUNITY_Dark Fantasy Image|Dark Fantasy Image]]
- [[_COMMUNITY_Dashboard Study Metrics|Dashboard Study Metrics]]
- [[_COMMUNITY_Linux Java Alternatives|Linux Java Alternatives]]
- [[_COMMUNITY_Teacher Registration|Teacher Registration]]
- [[_COMMUNITY_Database Schema Setup|Database Schema Setup]]

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 22 edges
2. `Moonlit Mountain Landscape` - 9 edges
3. `generate_gemini_text()` - 8 edges
4. `Linux` - 7 edges
5. `is_gemini_quota_error()` - 6 edges
6. `build_month_heatmap()` - 5 edges
7. `Java 8` - 5 edges
8. `Mac Balanced Image` - 5 edges
9. `Crowned Masked Figure` - 5 edges
10. `generate_study_assistant_reply()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `build_month_heatmap()` --calls--> `get_db()`  [EXTRACTED]
  app.py → app.py  _Bridges community 1 → community 7_
- `get_user_study_context()` --calls--> `get_db()`  [EXTRACTED]
  app.py → app.py  _Bridges community 1 → community 2_
- `teacher_register()` --calls--> `get_db()`  [EXTRACTED]
  app.py → app.py  _Bridges community 1 → community 9_
- `delete_material()` --calls--> `get_db()`  [EXTRACTED]
  app.py → app.py  _Bridges community 1 → community 0_
- `Linux` --references--> `Java 8`  [EXTRACTED]
  uploads/README-EN.txt → uploads/README-EN.txt  _Bridges community 4 → community 5_

## Hyperedges (group relationships)
- **Linux Launcher Execution Requirements** — readme_en_linux, readme_en_executable_permission, readme_en_java_runtime, readme_en_javafx, readme_en_tlauncher_jar [EXTRACTED 1.00]
- **Java Version Compatibility Guidance** — readme_en_tlauncher_jar, readme_en_java_8, readme_en_java_9_or_10, readme_en_rationale_java_8_compatibility [EXTRACTED 1.00]
- **Distribution Specific Package Installation** — readme_en_arch_linux, readme_en_debian_mint, readme_en_fedora_centos, readme_en_pacman, readme_en_apt, readme_en_yum [EXTRACTED 1.00]
- **Dark Fantasy Portrait Composition** — mac_balanced_crowned_masked_figure, mac_balanced_spiked_crown, mac_balanced_face_obscuring_hand, mac_balanced_cool_rim_lighting, mac_balanced_dark_fantasy_mood [INFERRED 0.84]
- **Minimal Wallpaper Layout** — mac_balanced_black_negative_space, mac_balanced_low_center_composition, mac_balanced_crowned_masked_figure, mac_balanced_wallpaper_like_layout [INFERRED 0.76]
- **Night Landscape Elements** — image2_full_moon, image2_starry_night_sky, image2_layered_clouds, image2_snow_capped_mountains, image2_central_stream, image2_silhouetted_trees, image2_purple_wildflower_meadow [EXTRACTED 1.00]
- **Selective Color Design** — image2_monochrome_palette, image2_selective_purple_accent, image2_purple_wildflower_meadow [EXTRACTED 1.00]
- **Layered Perspective Structure** — image2_purple_wildflower_meadow, image2_central_stream, image2_snow_capped_mountains, image2_starry_night_sky [INFERRED 0.85]

## Communities

### Community 0 - "Core Flask Routes"
Cohesion: 0.17
Nodes (7): class_chat(), delete_material(), get_active_seconds(), log_startup_configuration(), mask_secret(), private_chat(), teacher_login()

### Community 1 - "User Study Materials"
Cohesion: 0.15
Nodes (13): download_material(), edit_material(), get_db(), get_private_messages(), login(), pause_study(), register(), start_study() (+5 more)

### Community 2 - "Gemini Study AI"
Cohesion: 0.21
Nodes (13): ask_ai(), build_gemini_quota_message(), generate_gemini_text(), generate_study_assistant_reply(), generate_studyai_chat_reply(), generate_studyai_questions(), generate_studyai_summary(), get_gemini_model_candidates() (+5 more)

### Community 3 - "Moonlit Landscape Image"
Cohesion: 0.22
Nodes (13): Central Stream, Layered Depth Composition, Fantasy Night Illustration, Full Moon, Layered Clouds, Mostly Monochrome Palette, Moonlit Mountain Landscape, Purple Wildflower Meadow (+5 more)

### Community 4 - "Linux Launcher Setup"
Cohesion: 0.25
Nodes (11): apt, apt-get, Debian/Mint, Executable Permission, GPU Graphics Problems, Java Runtime, JavaFX, Linux (+3 more)

### Community 5 - "Java Mac Compatibility"
Cohesion: 0.25
Nodes (9): Arch Linux, Java 8, Java 9 or 10, https://java.com/, MacOS, pacman, Rationale: Use Java 8 For Launcher Compatibility, Rationale: Override OS Protection To Launch Unidentified Developer App (+1 more)

### Community 6 - "Dark Fantasy Image"
Cohesion: 0.36
Nodes (9): Black Negative Space, Cool Rim Lighting, Crowned Masked Figure, Dark Fantasy Mood, Face Obscuring Hand, Mac Balanced Image, Low Center Composition, Spiked Crown (+1 more)

### Community 7 - "Dashboard Study Metrics"
Cohesion: 0.5
Nodes (4): build_month_heatmap(), dashboard(), get_study_level(), heatmap_data()

### Community 8 - "Linux Java Alternatives"
Cohesion: 0.67
Nodes (4): Fedora/CentOS, Java 11, update-alternatives, yum

### Community 9 - "Teacher Registration"
Cohesion: 1.0
Nodes (2): generate_class_code(), teacher_register()

### Community 10 - "Database Schema Setup"
Cohesion: 1.0
Nodes (0): 

## Ambiguous Edges - Review These
- `Mac Balanced Image` → `Wallpaper Like Layout`  [AMBIGUOUS]
  uploads/mac_balanced.jpg · relation: conceptually_related_to

## Knowledge Gaps
- **10 isolated node(s):** `Executable Permission`, `GPU Graphics Problems`, `pacman`, `yum`, `https://java.com/` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Teacher Registration`** (2 nodes): `generate_class_code()`, `teacher_register()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Database Schema Setup`** (1 nodes): `create_db.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Mac Balanced Image` and `Wallpaper Like Layout`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Linux` connect `Linux Launcher Setup` to `Java Mac Compatibility`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `Java 8` connect `Java Mac Compatibility` to `Linux Launcher Setup`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Why does `get_db()` connect `User Study Materials` to `Core Flask Routes`, `Teacher Registration`, `Gemini Study AI`, `Dashboard Study Metrics`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Moonlit Mountain Landscape` (e.g. with `Fantasy Night Illustration` and `Tranquil Mood`) actually correct?**
  _`Moonlit Mountain Landscape` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Executable Permission`, `GPU Graphics Problems`, `pacman` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._