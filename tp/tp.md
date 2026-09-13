# La entrada en backwardation de la curva de futuros del VIX como señal de estrés en el mercado accionario estadounidense

---

# 1. Hipótesis

## 1.1. El concepto de volatilidad

La volatilidad es la medida de riesgo por excelencia en el análisis de activos financieros. En términos matemáticos representa la raíz cuadrada de la varianza de los rendimientos, es decir, la dispersión de un activo alrededor de su valor esperado; en términos económicos, refleja el grado de incertidumbre que perciben los participantes del mercado. Cuando las expectativas son estables, los precios fluctúan dentro de rangos moderados; cuando aparece información adversa o aumenta la incertidumbre, la volatilidad puede elevarse rápidamente.

El interés en esta pregunta no es solamente académico. Un aumento abrupto y persistente de la incertidumbre financiera afecta a las empresas por varias vías: eleva el costo de capital, ya que los inversores exigen una prima de retorno superior cuando perciben mayor riesgo, lo que reduce el valor presente de los flujos de fondos futuros y las valuaciones bursátiles; desalienta decisiones de inversión de largo plazo, que se vuelven menos atractivas cuando aumenta la incertidumbre sobre la demanda, el financiamiento o las condiciones macroeconómicas; y deteriora la liquidez de mercado, ampliando las puntas compradoras-vendedoras y encareciendo el financiamiento. La interacción entre menores valuaciones, condiciones financieras más restrictivas y menor confianza puede retroalimentar el ciclo económico y agravar una situación de distress. La importancia de estudiar la curva del VIX no radica en que la volatilidad cause por sí sola una crisis, sino en que podría anticipar un entorno financiero que afecte el valor y las decisiones de las compañías — y, en consecuencia, resultar útil como insumo para decisiones de cobertura o de inversión.

## 1.2. El VIX y la volatilidad implícita

La medida más utilizada para observar la volatilidad esperada del mercado accionario estadounidense es el Chicago Board Options Exchange Volatility Index (VIX), construido a partir de los precios de opciones sobre el S&P 500 y que representa una medida de volatilidad implícita para un horizonte aproximado de 30 días. Debido a que suele aumentar durante las correcciones bursátiles, se lo conoce habitualmente como "índice del miedo" (Whaley, 2000). El VIX no predice la dirección del mercado — un nivel elevado indica que se esperan movimientos de mayor magnitud, no necesariamente negativos —, pero empíricamente reacciona de forma asimétrica: con más fuerza ante caídas que ante subidas del S&P 500 (Whaley, 2009).

El VIX es una medida derivada de los precios de opciones sobre el S&P 500. A diferencia de la volatilidad histórica, calculada a partir de rendimientos pasados, la volatilidad implícita surge de los precios actuales del mercado y refleja la variabilidad futura que esos precios tienen incorporada. Cuando los inversores esperan movimientos más intensos, las primas de las opciones tienden a aumentar, y ese incremento se traduce en un VIX más elevado. El índice incorpora así tanto expectativas de variabilidad futura como la prima que exigen quienes asumen el riesgo de volatilidad — los compradores de protección suelen pagar por encima de la pérdida promedio esperada, especialmente cuando el seguro frente a eventos extremos es más valioso, por lo que un VIX elevado también puede reflejar mayor aversión al riesgo, no solo mayor volatilidad esperada.

Metodológicamente, el CBOE calcula el VIX replicando el valor de una cartera teórica de opciones out-of-the-money sobre el S&P 500 con vencimientos cercanos a 30 días, ponderadas de forma que su valor agregado aproxime la varianza esperada del índice bajo el enfoque de un swap de varianza. No es, entonces, la volatilidad implícita de una única opción, sino un promedio ponderado a lo largo de todo el espectro de precios de ejercicio cotizados, lo que lo hace menos sensible a distorsiones de una opción puntual y más representativo del consenso agregado del mercado sobre la volatilidad esperada.

## 1.3. Los futuros del VIX y su estructura temporal

El nivel spot del VIX solo informa sobre la volatilidad esperada de corto plazo. La introducción de los futuros del VIX en 2004 permitió observar cómo el mercado distribuye sus expectativas de volatilidad en distintos horizontes, formando una estructura temporal o "curva". Los futuros del VIX son contratos liquidados en efectivo cuyo valor está vinculado al VIX correspondiente a cada fecha de vencimiento. Al existir varios contratos con distintos vencimientos, sus precios pueden ordenarse por plazo restante. Denominando F₁,ₜ, F₂,ₜ, F₃,ₜ y F₄,ₜ a los contratos primero, segundo, tercero y cuarto en el día t, una curva ascendente presenta aproximadamente:

F₁,ₜ < F₂,ₜ < F₃,ₜ < F₄,ₜ (contango)

y una curva invertida:

F₁,ₜ > F₂,ₜ > F₃,ₜ > F₄,ₜ (backwardation)

Una curva ascendente indica que los vencimientos lejanos cotizan por encima de los cercanos — la situación habitual —, mientras que una curva invertida indica que la volatilidad de corto plazo está valorada por encima de la de plazos más largos, algo que suele ocurrir ante una demanda excepcional de cobertura inmediata frente al miedo o la incertidumbre. La curva no es solo una secuencia de pronósticos puntuales: sus precios incorporan primas de riesgo que varían según el vencimiento. Una pendiente negativa puede explicarse por dos mecanismos complementarios: (i) el mercado espera que la volatilidad actualmente elevada disminuya, y/o (ii) los participantes exigen una prima superior por asumir exposición a la volatilidad de corto plazo. Fassas y Hourvouliades (2019) estiman esta estructura mediante una regresión lineal diaria del VIX spot y siete futuros sobre su tiempo al vencimiento, usando toda la curva disponible; este trabajo simplifica esa estimación y utiliza únicamente dos puntos de la curva — el primer y el cuarto futuro — dado que el tiempo al vencimiento de cada contrato no estaba disponible en la fuente utilizada para las series continuas sin trabajo adicional de identificación de contratos con fecha real.

En términos de mecánica de mercado, los futuros del VIX vencen mensualmente y se liquidan en efectivo contra el valor del VIX en el momento del vencimiento. El primer contrato (F₁) es siempre el de vencimiento más próximo; al vencer, el segundo contrato pasa a ser el primero, y así sucesivamente — la convención de "futuro continuo" (utilizada en este trabajo bajo los códigos VXc1, para F₁, y VXc4, para el cuarto vencimiento) sigue automáticamente esta rotación. Empíricamente, la curva se encuentra en contango la mayor parte del tiempo: los vendedores de protección exigen una prima por los vencimientos lejanos, y en ausencia de un shock de corto plazo no hay motivo para que el mercado valore más el riesgo inmediato que el futuro. La backwardation es, por eso, la excepción — lo que la vuelve, a priori, una señal con contenido informativo si aparece de forma sistemática antes de episodios de estrés, y no simplemente ruido de mercado.

## 1.4. Razones económicas para analizar la inversión de la curva

Demanda de cobertura inmediata: cuando aumenta la preocupación por una caída del mercado, los inversores demandan protección y exposición positiva a la volatilidad, concentrada inicialmente en los vencimientos más cercanos —los que cubren el período percibido como una amenaza. Si esa presión compradora es suficientemente intensa, los futuros cercanos suben más rápido que los lejanos: la curva primero se aplana y luego se invierte.

Aversión al riesgo y prima de volatilidad: el precio de la protección también depende de cuánto valoran los inversores esa cobertura en escenarios adversos. Durante períodos de tensión, un instrumento que gana valor cuando el mercado cae puede volverse especialmente valioso, empujando su precio por encima de lo que indicaría la volatilidad histórica.

Cambio de régimen: el paso de contango a backwardation puede interpretarse como una ruptura del patrón habitual del mercado de volatilidad, en el que normalmente los plazos lejanos cotizan por encima de los cercanos.

## 1.5. Pregunta de investigación e hipótesis

Pregunta: el día en que la curva de futuros del VIX pasa de contango a backwardation, ¿aumenta la probabilidad de que el S&P 500 sufra un episodio de estrés financiero en los 20 días hábiles posteriores, respecto de un día cualquiera de la muestra?

Hipótesis nula (H0): la entrada en backwardation de la curva de futuros del VIX no aporta información relevante sobre la probabilidad de estrés financiero posterior, respecto del comportamiento habitual del mercado.

Hipótesis alternativa (H1): la entrada en backwardation incrementa la probabilidad de estrés financiero posterior respecto del comportamiento habitual del mercado.

A diferencia de un enfoque que buscara demostrar capacidad predictiva "perfecta", este trabajo entiende H1 en un sentido más modesto: que la señal aporta información suficientemente consistente como para ser considerada en una decisión de inversión, no que anticipe con certeza cada episodio de estrés.

Alcance y limitaciones de la pregunta: no se pretende establecer una relación causal entre la forma de la curva de futuros del VIX y el comportamiento del S&P 500 — ambos son, muy probablemente, manifestaciones simultáneas de un mismo cambio en la percepción de riesgo del mercado, más que uno la causa del otro. Tampoco se propone, en esta etapa, una estrategia de inversión completamente especificada y backtesteada con costos de transacción, tamaño de posición y gestión de riesgo; el objetivo es más acotado: determinar si existe una asociación suficientemente consistente entre la señal y el resultado posterior como para justificar, en un trabajo futuro, el diseño de una regla operable.

## 1.6. Definición operativa de estrés financiero

Para evitar seleccionar crisis históricas de forma discrecional —lo que introduciría subjetividad y reduciría la muestra a un número insuficiente de casos—, se define estrés financiero de forma cuantitativa a partir de variables observables del S&P 500.

Existe un episodio de estrés financiero en la fecha t si, durante los veinte días hábiles posteriores, se cumple al menos una de estas condiciones:

- El S&P 500 registra un máximo drawdown igual o superior al 5%.
- La volatilidad realizada anualizada supera el percentil 90 de su distribución histórica y el rendimiento acumulado del índice en la ventana es negativo.

Formalmente:

DDStressₜ,ₜ₊₂₀ = 1 si MDDₜ,ₜ₊₂₀ ≤ −5%; 0 en caso contrario

MDDₜ,ₜ₊₂₀ = mín (u∈[t,t+20]) [ Pᵤ / máx(s∈[t,u]) Pₛ − 1 ]

RVStressₜ,ₜ₊₂₀ = 1 si RVₜ,ₜ₊₂₀ > P90ₜ(RV) y Rₜ,ₜ₊₂₀ < 0; 0 en caso contrario

Stressₜ,ₜ₊₂₀ = máx(DDStressₜ,ₜ₊₂₀, RVStressₜ,ₜ₊₂₀)

La condición de rendimiento negativo en RVStress excluye los períodos de alta volatilidad acompañados de un desempeño positivo (por ejemplo, un rally muy fuerte), que no deberían contarse como estrés. El umbral P90ₜ(RV) se calcula únicamente con información disponible hasta la fecha t (una serie de volatilidad realizada *trailing*, es decir, mirando hacia atrás), de modo que no incorpore información futura.

La elección de veinte días hábiles (aproximadamente un mes calendario) busca equilibrar dos riesgos: una ventana demasiado corta captura solo movimientos de muy corto plazo, posiblemente ruido, mientras que una ventana demasiado larga diluye la relación entre la señal y el resultado. El umbral de −5% corresponde a una corrección moderada pero clara, y el percentil 90 sigue la misma lógica que Fassas y Hourvouliades (2019): identificar el 10% de las observaciones históricas más extremas, en vez de un umbral absoluto que perdería sentido al comparar épocas de mercado con niveles de volatilidad estructuralmente distintos.

## 1.7. La señal: entrada en backwardation y su intensidad

### 1.7.1. Por qué un único punto de decisión

Una decisión de inversión basada en esta señal solo puede tomarse con la información disponible el día en que la curva se invierte. Cualquier variable que dependa de cómo evoluciona el episodio hacia adelante — su duración final, su profundidad promedio a lo largo de todo el episodio — no está disponible en ese momento y, por lo tanto, no puede formar parte de una regla operable en tiempo real. Este trabajo evita expresamente ese tipo de variables y se limita a dos elementos: el evento de entrada, y la intensidad medida exclusivamente ese mismo día.

### 1.7.2. Definición de la pendiente

La pendiente diaria de la curva se calcula con el primer y el cuarto futuro (F₁ y F₄), en vez de los dos contratos consecutivos más cercanos, normalizada por el nivel contemporáneo del VIX spot para que sea comparable entre regímenes de volatilidad distintos:

βₜ = (F₄,ₜ − F₁,ₜ) / VIXₜ

Como F₄ vence después que F₁, el signo de βₜ replica el de la curva: βₜ ≥ 0 indica contango, βₜ < 0 indica backwardation. Se prefirió esta separación más amplia (F₁ vs. F₄, en vez de F₁ vs. F₂) para que la pendiente capture una porción mayor de la estructura temporal de la curva: dos contratos consecutivos pueden invertirse por un movimiento de precio pequeño y transitorio (por ejemplo, ruido cerca del vencimiento del contrato F₁), mientras que una inversión entre el primer y el cuarto vencimiento exige un desplazamiento más consistente de todo el tramo corto de la curva. Esto tiene un costo: menos días califican como "entrada en backwardation" (la inversión debe ser más profunda para invertir el signo de una diferencia más ancha), por lo que la muestra de eventos resultante es más chica pero, en principio, más limpia.

### 1.7.3. El evento

EntryBackwardationₜ = 1 si βₜ < 0 y βₜ₋₁ ≥ 0; 0 en caso contrario

Es el único momento de decisión del análisis: no se generan señales adicionales mientras dura el mismo episodio, evitando contar días consecutivos de una misma inversión como si fueran eventos independientes.

### 1.7.4. Intensidad de la señal

Intensidadₜ = −βₜ, evaluada únicamente en el día donde EntryBackwardationₜ = 1

Cuanto más negativo es βₜ ese día, mayor la intensidad. Esta variable continua permite preguntar directamente si las entradas más profundas se asocian con resultados posteriores más severos, sin necesidad de agrupar los eventos en categorías de intensidad baja/media/alta.

## 1.8. Qué regresión podríamos armar: el diseño metodológico

### 1.8.1. Grupo de comparación (baseline)

Para saber si el resultado observado después de una entrada en backwardation es distinto del comportamiento habitual del mercado, se necesita un grupo de referencia. En vez de comparar contra "días de contango" específicamente, se optó por una muestra de referencia incondicional: cualquier día de la serie, sin filtrar por régimen de la curva.

Esta muestra de referencia incluye todos los días de la serie con resultado a 20 días calculable, sin ningún espaciado ni filtro adicional — lo mismo que se hace con los eventos de entrada en backwardation: una regla de trading real actuaría en cada señal tal como ocurrió, y este trabajo aplica el mismo criterio a la referencia, en vez de descartar observaciones para ajustarlas a una construcción estadística más prolija.

Esto tiene un costo que se reconoce explícitamente: los resultados a 20 días de dos fechas consecutivas comparten casi la misma ventana futura, por lo que un mismo evento de mercado queda representado en las ventanas de muchos días consecutivos de la referencia — no es una colección de observaciones independientes, sino una serie con alta autocorrelación por construcción. Los promedios de la Sección 3.1 deben leerse, entonces, como una descripción del comportamiento típico de una ventana de 20 días en la muestra completa, no como el resultado de una prueba estadística formal sobre observaciones independientes.


### 1.8.2. Regresión logística: ¿se puede predecir el estrés financiero?

Se plantea directamente la pregunta de clasificación que motiva todo el trabajo: ¿se puede predecir, con la información disponible el día de la entrada, si los 20 días hábiles siguientes van a calificar como estrés financiero o no? El modelo, restringido a los días de entrada en backwardation, es:

P(Stressₜ,ₜ₊₂₀ = 1) = Λ[γ₀ + γ₁·Intensidadₜ + γ₂·VIXₜ + γ₃·Rᵖʳᵉₜ + γ₄·RVᵖʳᵉₜ]

donde Λ es la función logística, y `Rᵖʳᵉₜ` y `RVᵖʳᵉₜ` son, respectivamente, el retorno acumulado y la volatilidad realizada anualizada en los veinte días hábiles *anteriores* a la entrada — variables de control conocidas en t, calculadas de forma análoga a los resultados de la Sección 1.6 pero mirando hacia atrás en vez de hacia adelante. Todos los regresores son observables el día de la señal; la variable dependiente (`Stressₜ,ₜ₊₂₀`, definida en la Sección 1.6) es estrictamente posterior a t.

El logit permite evaluar dos cosas por separado: (i) si los coeficientes son estadísticamente significativos (¿hay una relación sistemática entre cada variable y la probabilidad de estrés?), y (ii) qué tan bien predice el modelo en la práctica — medido con la precisión de clasificación fuera de muestra (accuracy y AUC-ROC obtenidos por validación cruzada de 5 particiones, en vez del ajuste dentro de la misma muestra usada para estimar el modelo, que sobreestimaría la capacidad predictiva real dado el tamaño chico de la muestra). Esa precisión se compara, además, contra la regla trivial de predecir siempre la clase mayoritaria ("nunca va a haber estrés") — el piso que cualquier modelo con información real debería superar.

---

# 2. Obtención de datos

## 2.1. Refinitiv / LSEG Workspace: futuros del VIX

Los precios de los futuros del VIX (F₁ y F₄, bajo los códigos continuos VXc1 y VXc4) se obtuvieron a través de LSEG Workspace, la plataforma de datos de mercado de Refinitiv, utilizando un proyecto propio (`financial-engineering`) desarrollado para este fin.

Requisitos. Se necesita una cuenta activa de LSEG Workspace, la aplicación de escritorio instalada y abierta con sesión iniciada, y un *App Key* — un código que identifica a la aplicación frente a LSEG (no es la contraseña de la cuenta), generado desde el *App Key Generator* de LSEG con permisos habilitados para Side by Side API, EDP API y Eikon Data API.

Cómo funciona la conexión. El proyecto utiliza la librería oficial LSEG Data for Python (`import lseg.data as ld`). Cuando LSEG Workspace está abierto con sesión iniciada, crea automáticamente un proxy local en la computadora — un intermediario entre cualquier programa en Python y los servicios de LSEG, que permite reutilizar la sesión ya autenticada en Workspace sin iniciar sesión por separado desde el código. El flujo de conexión es:

1. Se lee el App Key desde un archivo de configuración local (`.env`).
2. Se crea una sesión con `ld.session.desktop.Definition(app_key=...).get_session()`.
3. El proyecto busca el proxy local probando los puertos del `9000` al `9060`, consultando el endpoint `/api/status` de cada uno hasta encontrar una respuesta que indique que el proxy está listo (normalmente se encuentra en el puerto 9000, pero el rango de búsqueda evita fallos si ese puerto está ocupado).
4. Encontrado el puerto correcto, se abre la sesión (`session.open()`) y se la fija como sesión por defecto (`ld.session.set_default(session)`).
5. Se solicitan los datos históricos con `ld.get_history(universe=[...], fields=[...], interval="1D", start=..., end=...)`, indicando los instrumentos (en este caso, `VXc1` y `VXc4`), el intervalo diario y el rango de fechas.
6. La respuesta se guarda en un archivo CSV y la sesión se cierra (`session.close()`).

Si LSEG Workspace está cerrado, sin sesión iniciada, o no llega a inicializar el proxy, la conexión falla — es una dependencia dura del programa de escritorio, no solo de las credenciales.

Los campos utilizados. Para cada contrato de futuro, `ld.get_history` puede devolver varios campos; este trabajo utiliza `SETTLE` (precio de liquidación diario) en lugar de `TRDPRC_1` (último precio operado), porque el precio de liquidación tiene menos datos faltantes — se define todos los días hábiles aunque no haya habido operaciones sobre el contrato ese día, mientras que el último precio operado puede faltar en jornadas de bajo volumen.

## 2.2. Yahoo Finance: VIX spot y S&P 500

El VIX spot y el S&P 500 no estaban disponibles en la cuenta de LSEG utilizada, por lo que se obtuvieron de Yahoo Finance mediante la librería `yfinance` de Python, bajo los tickers `^VIX` y `^GSPC` respectivamente. La descarga se realiza con una única llamada:

```python
yf.download(["^VIX", "^GSPC"], start=fecha_inicio, end=fecha_fin, interval="1d")
```

que devuelve los precios de cierre diarios de ambos instrumentos para el rango de fechas solicitado, sin necesidad de autenticación ni de ninguna aplicación de escritorio abierta — a diferencia de Refinitiv, es una consulta pública contra la API de Yahoo Finance. Los datos se guardan en un CSV con las columnas `Date, SP500, VIX`, alineado por fecha con el archivo de futuros de la Sección 2.1.

## 2.3. Unificación de las fuentes

Las dos fuentes (Refinitiv y Yahoo Finance) se combinan en un único dataset mediante una unión por fecha (`merge` externo sobre la columna `Date`), sin ningún preprocesamiento adicional en esta etapa — ni relleno de datos faltantes, ni cálculo derivado. El resultado es la base cruda sobre la que se calculan, en un paso posterior, todas las variables descriptas en la Sección 1 (βₜ, `EntryBackwardationₜ`, `Intensidadₜ`, y los resultados a 20 días). Todo el proceso se implementó como scripts de Python independientes y reproducibles, de modo que cualquier parámetro del diseño pueda modificarse y volver a correrse sobre la misma base sin rehacer los cálculos a mano.

La muestra final cubre del 10 de septiembre de 2007 al 9 de septiembre de 2026 (4784 observaciones diarias), lo que incluye la crisis financiera de 2008, la crisis de deuda europea de 2011, la corrección de 2015-2016, la corrección de 2018, la pandemia de 2020 y la corrección de 2022. Los futuros del VIX cotizan desde marzo de 2004; en principio la muestra podría extenderse unos años más atrás, aunque no se intentó en esta etapa del trabajo. Sobre esta base se identificaron 106 eventos de entrada en backwardation con resultado a 20 días calculable.

---

# 3. Resultados

## 3.1. Comparación descriptiva: eventos vs. grupo de referencia

Tabla 1. Resultado a 20 días hábiles — eventos vs. grupo de referencia

| Grupo | n | % con estrés | Retorno medio | Retorno mediano | Drawdown medio |
|---|---|---|---|---|---|
| Referencia (todos los días, sin espaciar) | 4698 | 25.2% | +0.83% | +1.47% | −4.06% |
| Eventos (entrada en backwardation, F₁ vs. F₄) | 106 | 42.5% | +0.64% | +1.59% | −5.27% |

La entrada en backwardation muestra una brecha clara respecto del grupo de referencia en frecuencia de estrés (42.5% frente a 25.2%, un riesgo relativo de ≈1.69) y en drawdown promedio (−5.27% frente a −4.06%). El retorno promedio, en cambio, no es marcadamente positivo: +0.64% frente al +0.83% del grupo de referencia, es decir, prácticamente en línea con el comportamiento habitual del mercado. El retorno mediano (+1.59% frente a +1.47%) tampoco muestra una diferencia relevante entre ambos grupos. En conjunto, la señal produce una lectura consistente con la hipótesis original —más estrés y peor drawdown— sin el contrapeso de un retorno promedio claramente favorable, aunque el efecto sobre el retorno no constituye una señal direccional clara en ningún sentido.

## 3.2. Distribución temporal y casos ilustrativos

Los 106 eventos con resultado calculable no se distribuyen de manera uniforme a lo largo de la muestra: se concentran en años de mayor tensión de mercado. La crisis financiera global aporta 9 eventos en 2008 (y 7 más en 2007 y 7 en 2009); la pandemia aporta 10 eventos en 2020; 2015 y 2022 aportan 9 y 8 eventos respectivamente. En contraste, años de mercado relativamente calmo (2012, 2016, 2017) registran entre 1 y 3 eventos.

Tres casos ilustran el patrón de la Sección 3.1:

- 11 de septiembre de 2008, cuatro días antes de la quiebra de Lehman Brothers: intensidad moderada (β = −0.0062), seguida de un retorno de −27.2% y un drawdown de −27.5% en 20 días — el escenario que la hipótesis buscaba anticipar. El evento previo, dos días antes (9 de septiembre), muestra el mismo patrón (−18.6% de retorno, −20.6% de drawdown).
- 24 de febrero de 2020, al inicio de la corrección por COVID-19: intensidad moderada (β = −0.068), seguida de un retorno de −30.6% — el peor resultado posterior de toda la muestra.
- 11 de junio de 2020, en plena recuperación post-COVID: la entrada más intensa de toda la muestra (β = −0.136, muy por encima del resto de los eventos), seguida de un retorno de +6.1% y sin activación del indicador de estrés. La inversión más profunda registrada no derivó en el peor resultado, sino en uno tranquilo.

## 3.3. Regresión logística: resultados

Tabla 2. P(Stressₜ,ₜ₊₂₀=1) explicado por Intensidadₜ, VIXₜ, Rᵖʳᵉₜ y RVᵖʳᵉₜ (n = 105, ajuste in-sample)

| Variable | Coeficiente | Error estándar | p-valor |
|---|---|---|---|
| Constante | −1.9915 | 0.881 | 0.024 |
| Intensidadₜ | +6.9516 | 7.541 | 0.357 |
| VIXₜ | +0.0278 | 0.045 | 0.535 |
| Rᵖʳᵉₜ | −6.1157 | 4.500 | 0.174 |
| RVᵖʳᵉₜ | +3.3002 | 4.049 | 0.415 |

Pseudo-R² de McFadden = 0.046; LLR (razón de verosimilitud del modelo completo) p-valor = 0.159.

Tabla 3. Precisión predictiva fuera de muestra (validación cruzada de 5 particiones)

| Métrica | Valor |
|---|---|
| Baseline ingenuo (predecir siempre "sin estrés") | 57.1% |
| Accuracy del modelo logístico | 56.2% |
| AUC-ROC | 0.612 |
| Recall sobre los casos que sí tuvieron estrés | 24% |

De los 45 eventos de la muestra que efectivamente terminaron en estrés financiero, el modelo identificó correctamente solo 11 (recall del 24%); de los 60 eventos que no terminaron en estrés, identificó correctamente 48.

## 3.4. Conclusión: el modelo no logra predecir el estrés financiero con utilidad práctica

El modelo de la Sección 3.3, en su conjunto, no es estadísticamente significativo (LLR p-valor = 0.159), y ninguno de los cuatro regresores lo es individualmente (todos los p-valores superan 0.17). El pseudo-R² de McFadden (0.046) confirma un poder explicativo muy bajo.

Más importante todavía: la precisión predictiva fuera de muestra del modelo (56.2%) es menor que la del baseline ingenuo de predecir siempre "no va a haber estrés" (57.1%). El modelo, en la práctica, no aporta ninguna capacidad de clasificación por encima de no usar ningún modelo. El AUC-ROC de 0.612 —apenas por encima de 0.5, el valor esperado por azar— confirma una capacidad discriminativa débil, y el recall de apenas 24% sobre los casos que sí tuvieron estrés muestra que el modelo pierde la gran mayoría de los episodios que buscaba anticipar.

En conjunto, la evidencia descriptiva de la Sección 3.1 sigue mostrando que el estrés es más frecuente después de una entrada en backwardation que en un día cualquiera. Pero esta sección responde una pregunta distinta y más exigente —¿se puede usar la intensidad de la señal, el nivel de VIX y las condiciones previas del mercado para predecir, caso por caso, si un episodio en particular va a terminar en estrés?— y la respuesta, con esta evidencia, es que no: ni la profundidad de la inversión el día de entrada, ni el nivel de VIX, ni el comportamiento reciente del mercado antes de la señal, permiten anticipar con precisión útil si un episodio de backwardation va a terminar siendo leve o severo. Esto es consistente con el caso ilustrado en la Sección 3.2: la entrada más intensa de toda la muestra (junio de 2020) no fue la que peor terminó — de hecho, ni siquiera activó el indicador de estrés.
