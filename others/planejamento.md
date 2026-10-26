# Planejamento do modelo de classificação e do teste adversarial

## 1. Modelo candidato

**Regressão Logística multiclasse.**

O problema formalizado na seção 10 do notebook é uma classificação multiclasse: o texto da mensagem (`Ticket Description`) deve ser associado a uma das cinco intenções de `Ticket Type`. A Regressão Logística é adequada porque:

- estima a probabilidade de cada uma das cinco classes e retorna a mais provável;
- funciona bem com a matriz esparsa e de alta dimensão gerada a partir do texto, em que cada palavra do vocabulário é uma coluna;
- treina rapidamente com os 8.469 tickets e responde rapidamente na rota `/predict`;
- é interpretável: os coeficientes mostram quais palavras aumentam ou diminuem a chance de cada intenção;
- as classes são balanceadas (19,29% a 20,69%), então não é necessário ajustar pesos por classe.

## 2. Estratégia de representação do texto

**CountVectorizer.**

O modelo precisa de atributos numéricos. O CountVectorizer cria um vocabulário com as palavras dos textos de treino e transforma cada mensagem em um vetor com a contagem de cada palavra (bag of words). A técnica foi escolhida porque:

- é simples, determinística e fácil de explicar: cada coluna corresponde a uma palavra do vocabulário;
- as mensagens são curtas e de tamanho homogêneo (21 a 67 palavras), então a contagem direta não é distorcida por textos muito longos;
- gera uma matriz esparsa compatível com a Regressão Logística;
- o vocabulário é aprendido somente no conjunto de treino, o que evita vazamento de dados, e o mesmo vetorizador treinado pode ser reutilizado pela API na rota `/predict`.

## 3. Alvo para o teste adversarial

API da equipe que será utilizada como alvo autorizado nas atividades de pentest do TP4/TP5:

**URL/IP:** `A_DEFINIR`
