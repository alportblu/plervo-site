# Plervo — site

Site estático independente: HTML/CSS e um módulo local que sugere o sistema do download. Sem analytics, cookies ou widgets externos. A sugestão usa informações básicas já expostas pelo navegador, não as transmite e não inicia downloads automaticamente. As três opções permanecem disponíveis; celulares e tablets recebem uma indicação de que o app é para computadores.

```sh
python3 build.py
python3 -m unittest -v
node --test tests/downloads.test.mjs
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```

Publicado na Cloudflare Pages Free em https://plervo.com, também disponível em https://www.plervo.com e https://plervo-site.pages.dev, usando Direct Upload do diretório `dist`. O domínio permanece registrado na GoDaddy e o DNS está na Cloudflare; ambos os domínios próprios foram verificados por HTTPS. O workflow `Plervo site checks` verifica a geração, os links, a proteção dos downloads e a sugestão de sistema em cada push e pull request. A branch `main` exige PR e esse check aprovado, inclusive para administradores.

A página `/seguranca/` aponta para o canal privado de relatos habilitado em `alportblu/plervo-pdf`, no GitHub. O site não recebe o conteúdo desses relatos.

`config.json` controla os links públicos. O apoio está configurado para `https://buymeacoffee.com/alport`, fornecido pelo proprietário e conferido no Chrome oficial em 14 de outubro de 2026: Ricardo Bonetti, criador do Plervo. A página `/apoiar/` abre o serviço somente quando o visitante escolhe o link. Downloads permanecem vazios até que cada pacote seja assinado quando aplicável, validado no sistema correspondente e publicado na release oficial. Nunca usar links de exemplo no ambiente público.

Não existem dados bancários, tokens de serviço ou chaves privadas neste projeto.

Identidade SVG e layout: originais do Plervo, criados para este projeto. Tipografia: fontes já disponíveis no dispositivo, sem arquivos de fonte distribuídos. Nenhum recurso gráfico da Adobe ou ArtCraft.
