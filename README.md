# Projeto de Bloco - TP3

Projeto desenvolvido por Junior, Matheus e Paulo para a disciplina Projeto de Bloco do curso de Análise e Segurança de Agentes de IA do Instituto Infnet.

## Objetivo

O projeto utiliza o [Customer Support Ticket Dataset](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset) como base para um sistema de atendimento ao cliente. A variável `Ticket Type` representa a intenção do usuário e `Ticket Description` é o texto usado como entrada.

O TP2 reuniu a análise exploratória completa dos dados e uma API FastAPI com persistência em SQLite, autenticação JWT, controle de acesso por proprietário, validação de entrada, rate limiting e headers HTTP de segurança.

O TP3 consolida o projeto: o notebook ganha uma regressão linear com análise de resíduos e a formalização do problema de classificação; a API passa a ter testes de segurança executados no GitHub Actions, rotas documentadas em `/docs` e uma auditoria final com OWASP ZAP; e o planejamento da próxima etapa fica em `others/planejamento.md`.

## Estrutura

```text
.github/workflows/testes.yml  Pipeline de CI com os testes
data/                         Dataset em CSV
eda/eda_tp3.ipynb             Notebook com o EDA completo do TP1, TP2 e TP3
fastapi/
  main.py                     Entrada da aplicação
  database.db                 Banco SQLite com dados de exemplo
  sqlite_database.py          Criação das tabelas e população inicial do banco
  sqlite_populate.py          População do banco com os dados de exemplo
  models/                     Modelos Pydantic e SQLModel
  routes/                     Rotas da API
  security/                   JWT, senhas e rate limiting
others/                       DFD da API e planejamento da próxima etapa
tests/                        Testes automatizados de segurança
zap/                          Relatório e análise do scan passivo
```

## Instalação

Requer Python 3.11 ou superior.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r fastapi/requirements.txt -r eda/requirements.txt
```

No Windows, a ativação do ambiente é feita com:

```powershell
.venv\Scripts\activate
```

## Configuração da chave JWT

A chave de assinatura não fica armazenada no código. Antes de iniciar a API, defina `JWT_SECRET` com pelo menos 32 caracteres:

```bash
export JWT_SECRET="uma-chave-local-com-pelo-menos-32-caracteres"
```

Em PowerShell:

```powershell
$env:JWT_SECRET="uma-chave-local-com-pelo-menos-32-caracteres"
```

O arquivo `.env.example` mostra o nome esperado da variável. Quando ela não é definida, a aplicação gera uma chave temporária válida somente durante o processo atual.

## Banco de dados

O repositório já contém `fastapi/database.db`. Para recriar o banco e popular os dados de exemplo:

```bash
cd fastapi
python sqlite_database.py --recriar
```

O `sqlite_database.py` cria as tabelas e chama `sqlite_populate.py` para inserir os dados de exemplo. Para popular novamente um banco já existente:

```bash
cd fastapi
python sqlite_populate.py
```

O banco contém dois usuários e predictions pertencentes a proprietários diferentes. As senhas são armazenadas com PBKDF2-SHA256.

| Usuário | Senha |
| --- | --- |
| `admin` | `infnet` |
| `usuario2` | `teste123` |

O script de criação usa `sqlite3`, conforme solicitado. As consultas feitas pelas rotas usam SQLModel.

## Execução da API

Dentro de `fastapi/`, execute:

```bash
uvicorn main:app --reload
```

A documentação interativa fica disponível em `http://127.0.0.1:8000/docs`. Cada rota possui descrição, corpo ou parâmetros esperados, respostas possíveis e indicação de autenticação. As rotas protegidas podem ser testadas pelo botão **Authorize**.

### Rotas principais

| Método | Rota | Proteção | Finalidade |
| --- | --- | --- | --- |
| GET | `/health` | Pública | Verifica se a API está ativa |
| POST | `/auth/token` | Credenciais | Retorna um token JWT |
| POST | `/predict` | Bearer token | Cria uma prediction para o usuário autenticado |
| GET | `/predictions/{id}` | Bearer token e ownership | Retorna apenas recursos do próprio usuário |

O endpoint de autenticação aceita no máximo dez requisições por minuto por cliente.

## Controles de segurança

- autenticação com OAuth2 Password Bearer e JWT com expiração;
- senhas armazenadas com salt e PBKDF2-SHA256;
- validação Pydantic com `extra="forbid"`;
- consultas da API com SQLModel;
- verificação de ownership contra BOLA;
- CORS limitado às origens locais configuradas;
- HSTS, X-Frame-Options, X-Content-Type-Options e Content-Security-Policy;
- rate limiting de 10 requisições por minuto em `/auth/token`;
- foreign keys habilitadas nas conexões SQLite.

## Testes

Na raiz do projeto, execute:

```bash
pytest tests/ -v
```

Os testes usam um banco temporário e cobrem:

- autenticação com credenciais válidas e inválidas;
- tentativa de acessar `/predict` sem token;
- tentativa de acessar uma prediction de outro usuário (BOLA);
- envio de campo extra no corpo da requisição;
- bloqueio por rate limiting após 10 requisições por minuto em `/auth/token`.

O workflow `.github/workflows/testes.yml` executa a mesma suíte no GitHub Actions a cada push e falha caso algum teste falhe.

## EDA

Para abrir o notebook:

```bash
cd eda
jupyter notebook eda_tp3.ipynb
```

O notebook contém inspeção, qualidade, limpeza, análises univariada e multivariada, correlações, associações categóricas, outliers, dois testes de hipótese Mann-Whitney e conclusões. No TP3, foram adicionadas a regressão linear com R², RMSE, Residual Plot e Q-Q Plot (seção 9) e a formalização do problema de classificação (seção 10).

## OWASP ZAP

Os artefatos do scan passivo ficam em `zap/`. A auditoria final do TP3 cobriu todas as rotas da API e a documentação `/docs`, e não encontrou findings Medium ou High. O arquivo `scan_passivo_zap_TP3.md` registra a execução, o resultado e como reproduzir o scan; o relatório exportado é `relatorio_zap_TP3.html`.

## Planejamento

O arquivo `others/planejamento.md` define o modelo candidato, a representação do texto com CountVectorizer e o alvo autorizado para o teste adversarial do TP4/TP5.

## DFD

O diagrama de fluxo de dados está em `others/dfd_api.png`. O arquivo editável `others/dfd_api.drawio` também foi mantido no repositório.
