# Análise do scan passivo OWASP ZAP - TP3

## Informações da execução

- Ferramenta: OWASP ZAP 2.17.0 (imagem Docker `zaproxy/zap-stable`), executado pelo Automation Framework
- Tipo: somente regras passivas, sem active scan
- Alvo: `http://host.docker.internal:8000`
- Data: 26/10/2026
- Relatório HTML: `zap/relatorio_zap_TP3.html`

No TP2, o scan partiu apenas de `/docs`. Nesta auditoria final, o scan também cobriu todas as rotas da API:

- importação de `/openapi.json`, que gera requisições para `/health`, `/auth/token`, `/predict` e `/predictions/{prediction_id}`;
- requisições autenticadas com token JWT para `POST /predict` e `GET /predictions/1`, para que as respostas 200 das rotas protegidas também fossem analisadas;
- spider a partir de `/docs`.

## Resultado

**A auditoria final não encontrou findings de severidade Medium ou High.** Por isso, não houve correções nesta etapa.

O relatório registrou:

- 0 findings High;
- 0 findings Medium;
- 0 findings Low;
- 2 observações Informational.

As duas observações foram:

- `Authentication Request Identified` (`10111`) em `POST /auth/token`: o ZAP apenas identifica a requisição de login. A rota já possui rate limiting de 10 requisições por minuto;
- `Modern Web Application` (`10109`) em `/docs`: classificação informativa da página Swagger, sem vulnerabilidade associada.

Os quatro findings Medium encontrados no TP2 em `/docs` (CSP sem `form-action`, `unsafe-inline` em `script-src` e em `style-src` e Subresource Integrity ausente) não voltaram a aparecer. As correções feitas naquela etapa continuam em `fastapi/main.py`.

## Como reproduzir

Com a API em execução em `fastapi/` (`uvicorn main:app --host 0.0.0.0 --port 8000`), gere um token em `/auth/token` e substitua `TOKEN` no plano abaixo:

```yaml
env:
  contexts:
    - name: api
      urls:
        - http://host.docker.internal:8000
      includePaths:
        - http://host.docker.internal:8000.*

jobs:
  - type: passiveScan-config
    parameters:
      scanOnlyInScope: true
  - type: openapi
    parameters:
      apiUrl: http://host.docker.internal:8000/openapi.json
      targetUrl: http://host.docker.internal:8000
      context: api
  - type: requestor
    requests:
      - url: http://host.docker.internal:8000/predict
        method: POST
        headers:
          - "Authorization: Bearer TOKEN"
          - "Content-Type: application/json"
        data: '{"texto": "Quero meu dinheiro de volta"}'
      - url: http://host.docker.internal:8000/predictions/1
        method: GET
        headers:
          - "Authorization: Bearer TOKEN"
  - type: spider
    parameters:
      context: api
      url: http://host.docker.internal:8000/docs
  - type: passiveScan-wait
  - type: report
    parameters:
      template: traditional-html
      reportDir: /zap/wrk
      reportFile: relatorio_zap_TP3
```

Execução:

```bash
docker run --rm -v "$(pwd):/zap/wrk:rw" zaproxy/zap-stable zap.sh -cmd -autorun /zap/wrk/plano.yaml
```
