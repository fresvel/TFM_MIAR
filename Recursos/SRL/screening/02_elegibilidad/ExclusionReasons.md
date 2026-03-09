# Catalogo de exclusion (Full Text) - SLR Calidad de Aire + Logica Difusa

## Alcance
Este catalogo se usa solo en la fase de elegibilidad por texto completo.
No usar estas razones para `Reports not retrieved` (eso va en su propia caja PRISMA).

## Convencion de decision
- Valores por criterio `FT_*_IEP`: `I` (incluye), `E` (excluye), `P` (pendiente).
- Si `FT_Final_decision=Exclude`, registrar exactamente **una** categoria en `FT_Exclusion_reason`.
- Toda exclusion debe tener evidencia breve en la columna `..._evidence` correspondiente (ideal: pagina/seccion).

## Categorias controladas (permitidas)
1. `D2-NoFuzzyCentral`
   - Definicion: la logica difusa no es el mecanismo central para evaluar calidad del aire.
   - Trigger: `FT_D2_fuzzy_inference_central_IEP = E`.

2. `D3-NoPlatformImplementation`
   - Definicion: no existe implementacion en sistema/plataforma de monitoreo o pipeline operacional.
   - Trigger: `FT_D3_platform_monitoring_implementation_IEP = E`.

3. `Transversal-NoEmpiricalValidation`
   - Definicion: no hay diseno metodologico claro y/o validacion cuantitativa empirica.
   - Trigger: `FT_Transversal_design_validation_IEP = E`.

4. `D1-NoVariablesOrPollutants`
   - Definicion: no especifica contaminantes/variables de entrada para la evaluacion.
   - Trigger: `FT_D1_variables_contaminants_IEP = E`.

5. `D2-NoModelStructure`
   - Definicion: no describe tipo de sistema difuso ni su estructura (reglas, funciones, arquitectura).
   - Trigger: `FT_D2_model_structure_type_design_IEP = E`.

6. `D3-NoSettingOrUnit`
   - Definicion: no define entorno de aplicacion ni unidad de analisis.
   - Trigger: `FT_D3_setting_unit_of_analysis_IEP = E`.

7. `NotPrimaryStudy`
   - Definicion: en full text se confirma que no es estudio primario (review, chapter, editorial, etc.).
   - Trigger: evidencia directa en texto completo (aunque haya pasado screening).

## Regla de prioridad (razon unica)
Si un estudio falla multiples criterios, usar la primera categoria aplicable:

1. `D2-NoFuzzyCentral`
2. `D3-NoPlatformImplementation`
3. `Transversal-NoEmpiricalValidation`
4. `D1-NoVariablesOrPollutants`
5. `D2-NoModelStructure`
6. `D3-NoSettingOrUnit`
7. `NotPrimaryStudy`

## Regla de registro en CSV
- `FT_Final_decision=Include` -> `FT_Exclusion_reason` vacio.
- `FT_Final_decision=Exclude` -> `FT_Exclusion_reason` obligatorio (una sola categoria del catalogo).
- `FT_Final_decision=Pending` -> `FT_Exclusion_reason` vacio.

## Checklist rapido por articulo
1. Completar los seis criterios `FT_*_IEP`.
2. Marcar evidencia textual en cada `..._evidence`.
3. Definir `FT_Final_decision`.
4. Si es `Exclude`, asignar una razon unica segun prioridad.
