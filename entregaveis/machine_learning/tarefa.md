# Tarefa de Machine Learning: regressão e classificação

Essa tarefa tem três partes. Nas duas primeiras vocês treinam dois modelos, uma de **regressão** e outra de **classificação**. Na terceira, gerar as previsões para os dados de teste que já estão no diretório e submetem no Kaggle.

A ideia não é só chamar `.fit()` e olhar o número que sai. É entender os dados antes, escolher a métrica certa para o problema, comparar mais de um algoritmo com um critério.

## O que vocês vão receber

```
entregaveis/machine_learning/
├── tarefa.md                 este arquivo
├── regressao/
│   ├── train.csv             395 alunos, 30 features + a coluna score (alvo)
│   ├── test.csv              20 alunos, mesmas 30 features, SEM a coluna score
│   └── student.txt           dicionário de dados, o que significa cada coluna
└── classiicacao/
    ├── train2.csv            569 amostras, a coluna diagnosis (alvo) + 30 features
    └── test2.csv             20 amostras, mesmas 30 features, SEM a coluna diagnosis
```

Os arquivos de teste **não têm a coluna alvo**. Isso é proposital: eles são o conjunto que vale nota no Kaggle. Vocês nunca vão saber a resposta certa deles, então toda a avaliação que vocês fizerem durante o desenvolvimento tem que sair de dentro do `train`.

Criem o notebook de vocês como `entregaveis/machine_learning/nome_sobrenome.ipynb`, seguindo o mesmo padrão das outras entregas do repositório.

Bibliotecas esperadas: `pandas`, `numpy`, `matplotlib`/`seaborn`, `scikit-learn`. Se quiserem usar `xgboost` ou `lightgbm` podem, ou ate modelos mais avançados como foundation models.

---

## Parte 1: Regressão — Student Performance

### O problema

O dataset é o **Student Performance** do UCI Machine Learning Repository, na versão do curso de **Matemática**. Cada linha é um aluno de uma escola, com informações demográficas, familiares e de hábitos de estudo.

A variável dependente é `score`, a nota média do aluno no curso de matemática:

```
score = mean(G1, G2, G3)
```

onde `G1` é a nota do primeiro período, `G2` a do segundo e `G3` a nota final, cada uma de 0 a 20. No `train.csv` o `score` varia de 0 a 20, com média em torno de 10.7. **É um número contínuo, por isso é um problema de regressão, não de classificação.**

Vejam o `student.txt` para o significado de cada uma das 30 colunas. Vale a pena ler antes de escrever qualquer código: várias colunas que parecem numéricas são na verdade categóricas ordenadas (`Medu`, `studytime`, `famrel`, `health` etc. são escalas de 1 a 5), e outras são texto (`Mjob`, `reason`, `guardian`).

### O que fazer

**1.1 Análise exploratória (EDA).**

**1.2 Limpeza e pré-processamento.** (se necessário)

**1.3 Modelo de inferência.**

Sugestões:

| Família               | Modelo                                 | `sklearn`                                   | Por que testar                                                                     |
| --------------------- | -------------------------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------- |
| Linear                | Regressão Linear                       | `LinearRegression`                          | _baseline_ simples e interpretável                                                 |
| Linear regularizada   | Ridge / Lasso / ElasticNet             | `Ridge`, `Lasso`, `ElasticNet`              | controlam _overfitting_; o Lasso ainda zera coeficientes e faz seleção de features |
| Baseada em distância  | KNN                                    | `KNeighborsRegressor`                       | não assume forma nenhuma para a relação; exige escala padronizada                  |
| Baseada em margem     | SVR                                    | `SVR`                                       | captura relações não lineares via kernel                                           |
| Árvore                | Árvore de Decisão                      | `DecisionTreeRegressor`                     | captura interações e não linearidades, mas sozinha costuma dar _overfitting_       |
| _Ensemble_ (bagging)  | Random Forest                          | `RandomForestRegressor`                     | várias árvores reduzem a variância; costuma ir muito bem sem ajuste fino           |
| _Ensemble_ (boosting) | Gradient Boosting / XGBoost / LightGBM | `GradientBoostingRegressor`, `XGBRegressor` | geralmente bom desempenho em dados tabulares                                       |

**1.4 Métrica de avaliação.** A métrica principal desta tarefa é o **RMSE (Root Mean Squared Error)**:

$$\text{RMSE} = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(y_i - \hat{y}_i)^2}$$

---

## Parte 2: Classificação — Breast Cancer

### O problema

O dataset é o **Breast Cancer Wisconsin (Diagnostic)**, também do UCI. Cada linha descreve o núcleo de células extraídas de uma massa mamária por punção aspirativa por agulha fina, e o alvo é o diagnóstico:

- `M` = **maligno** (tumor canceroso)
- `B` = **benigno** (tumor não canceroso)

São 30 features numéricas, formadas por 10 medidas do núcleo celular (`radius`, `texture`, `perimeter`, `area`, `smoothness`, `compactness`, `concavity`, `concave points`, `symmetry`, `fractal_dimension`), cada uma em três versões: `_mean` (média), `_se` (erro padrão) e `_worst` (média dos três piores valores).

No `train2.csv` há 569 amostras, 357 benignas e 212 malignas — ou seja, cerca de **63% / 37%**. As classes são desbalanceadas, mas de forma leve. Guardem esse número: ele é o seu piso de acurácia. Um modelo que responde "benigno" para tudo já acerta 63%, e isso não vale nada clinicamente.

### O que fazer

**2.1 Análise exploratória.**

**2.2 Pré-processamento.**

**2.3 Modelo de inferência.** sugestões:

| Modelo                      | `sklearn`                                     | Observação                                           |
| --------------------------- | --------------------------------------------- | ---------------------------------------------------- |
| Regressão Logística         | `LogisticRegression`                          | _baseline_ forte e interpretável; exige padronização |
| KNN                         | `KNeighborsClassifier`                        |                                                      |
| Naive Bayes                 | `GaussianNB`                                  | assume independência entre features                  |
| SVM                         | `SVC(probability=True)`                       | teste kernel linear e RBF                            |
| Árvore de Decisão           | `DecisionTreeClassifier`                      | fácil de visualizar e explicar                       |
| Random Forest               | `RandomForestClassifier`                      |                                                      |
| Gradient Boosting / XGBoost | `GradientBoostingClassifier`, `XGBClassifier` | forte em dados tabulares                             |

**2.4 Avaliação.**

- **Acurácia** — fração de acertos. Reportem, mas não parem nela: com classes desbalanceadas ela engana (lembrem do baseline de 63%).
- **Matriz de confusão** (`confusion_matrix` + `ConfusionMatrixDisplay`) — plotem e **interpretem**. Digam quantos são verdadeiros positivos, verdadeiros negativos, falsos positivos e falsos negativos.

---

## Parte 3: Submissão no Kaggle

Os arquivos `regressao/test.csv` e `classiicacao/test2.csv` **já estão neste diretório, sem as labels**. São eles que vocês vão prever e submeter.

[Tarefa de Regressão](https://www.kaggle.com/competitions/ufrj-analytica-training-ml)

[Tarefa de Classificação](https://www.kaggle.com/competitions/tarefa-de-machine-learning-classificacao)

```csv
id,score
0,11.42
1,8.07
...
```

```csv
id,diagnosis
0,0
1,1
2,0
3,0
...
```

Confiram no `sample_submission.csv` o nome exato das colunas, o tipo do `id` (índice começando em 0 ou em 1) e se `diagnosis` deve ser `1`/`0`. Uma submissão com o cabeçalho errado é rejeitada mesmo com o modelo perfeito.

Antes de submeter, abram o `submission.csv` e confiram três coisas: o número de linhas bate com o do arquivo de teste, não tem `NaN`, e os valores estão numa faixa plausível (nota entre 0 e 20 na regressão; só `M` e `B` na classificação).

### Sobre a métrica pública

A métrica do _leaderboard_ será **RMSE** na regressão e **acurácia** na classificação. Os conjuntos de teste têm apenas 20 linhas cada.

Bom trabalho.
