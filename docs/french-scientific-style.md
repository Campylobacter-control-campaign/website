# French scientific language guide / Guide de rédaction scientifique (FR)

**Audience:** French-speaking researchers and public-health collaborators in France and francophone West Africa. The French website should read like scientific communication written in French, **not** a literal translation of the English website.

## Preferred terminology

| Concept | Preferred French website usage | Avoid / use with care |
| --- | --- | --- |
| One Health | **One Health**; « approche One Health » | « Une seule santé » as the default label (legitimate in official French policy texts, but less idiomatic for this project's research audience) |
| Antimicrobial resistance | **antibiorésistance** when bacterial antibiotic resistance is intended; **résistance aux antimicrobiens (RAM)** when broader than antibiotics | using English **AMR** in a French role label without explanation |
| Source attribution | **attribution des sources**, « attribuer les isolats à leurs sources probables » | literal, vague « attribuer » without a source/object |
| Whole-genome sequencing | **séquençage du génome entier** | unnecessary English label in prose |
| Metagenomics | **métagénomique**, « analyses métagénomiques » | unnecessary English label |
| Machine learning | **apprentissage automatique**; « méthodes d’apprentissage automatique » | gratuitous English **machine learning** in French prose |
| Case-control recruitment | **cas de diarrhée**, **témoins communautaires**, **enfants témoins recrutés dans la communauté** where the study design supports it | « cas diarrhéiques » as a recurring label; confusing all community children with cases |
| Household members | **membres du ménage** | inconsistent alternation between « foyer » and « ménage » in cohort labels |
| Field sampling | **prélèvements**, **échantillonnage**, **collecte d’échantillons** according to context | translating every English *sample* as the same noun |
| Laboratory workflow | **procédures de laboratoire**, **circuit de prélèvement et d’analyse**, **chaîne analytique** | unqualified « workflow » |
| SOP | **procédures opératoires standardisées (SOP)** at first mention, then **SOP** | untranslated « SOP » without context for wider audiences |
| Culture-positive / PCR-positive | **positif en culture**, **positif en PCR**, **résultat positif** with explicit denominator | treating positive tests as distinct positive people without accounting for overlap |
| Repository | **entrepôt de données** for data archives; **dépôt GitHub** for code | calling a code repository an « entrepôt de données » |
| Country-specific sampling | **données agrégées par site**, **effectifs échantillonnés**, **résultats disponibles** | combining different denominators into a single prevalence |

## Scientific accuracy and style

- **Do not translate proper project names**: Campylobacter Control Campaign, GETCampy, PubMLST, protocols.io, REDCap, SurveyCTO.
- Italicise the genus *Campylobacter* in scientific prose, including French content.
- Prefer concise scientific prose, active verbs, and explicit subjects. Avoid repeated literal English syntactic structures.
- Preserve study-design distinctions: enrolled participants, collected specimens, tested specimens, positive assays, and distinct confirmed-positive participants are **not interchangeable**.
- When translating dynamically from `dashboard.json`, modify only display labels. **Never change data keys, counts, denominators, status values or scientific source notes in the canonical JSON.**
- Maintain the EN/FR page pair and the French homepage/dashboard dynamic UI when making further changes.
- Ask francophone collaborators to review disciplinary terminology, especially the wording of case/control recruitment and any locally specific clinical terms.

## Usage evidence

French research institutions use **One Health** extensively in scientific communication:
- Institut Pasteur, Santé globale: https://www.pasteur.fr/fr/nos-recherches/notre-approche-scientifique/nos-expertises-scientifiques/sante-globale
- Institut Pasteur, Graduate Schools: https://www.pasteur.fr/fr/nous-connaitre/nos-missions/lenseignement/formations/graduate-schools-0

**Nuance:** « Une seule santé » is **not incorrect French** and is also used in institutional and policy communication (for example by Anses and INRAE). CCC chooses **One Health** as its house style because its primary audience is academic:
- Anses: https://anses.fr/fr/content/one-health-une-seule-sante-pour-les-etres-vivants-et-les-ecosystemes
- INRAE: https://www.inrae.fr/alimentation-sante-globale/one-health-seule-sante

This guide is a project editorial convention, not a claim that French institutions never use the translated expression.
