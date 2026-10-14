# Plervo — site

Site estático independente: HTML/CSS, sem JavaScript no navegador, analytics, cookies ou widgets externos.

```sh
python3 build.py
python3 -m unittest -v
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```

Publicação prevista: Cloudflare Pages Free. Na Cloudflare, conectar o repositório com comando `python3 build.py` e diretório de saída `dist`, ou usar Direct Upload com esse diretório. O domínio permanece registrado na GoDaddy. Associar `plervo.com` e `www.plervo.com` somente depois de validar a implantação.

`config.json` controla os links públicos. O link do Buy Me a Coffee permanece vazio até o proprietário fornecer sua página verificada. Downloads permanecem vazios até que cada pacote seja assinado quando aplicável, validado no sistema correspondente e publicado na release oficial. Nunca usar links de exemplo no ambiente público.

Não existem dados bancários, tokens de serviço ou chaves privadas neste projeto.

Identidade SVG e layout: originais do Plervo, criados para este projeto. Tipografia: fontes já disponíveis no dispositivo, sem arquivos de fonte distribuídos. Nenhum recurso gráfico da Adobe ou ArtCraft.
