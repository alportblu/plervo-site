# Plervo — site

Site estático independente: HTML/CSS e um módulo local que sugere o sistema do download. Sem analytics, cookies ou widgets externos. A sugestão usa informações básicas já expostas pelo navegador, não as transmite e não inicia downloads automaticamente. As três opções permanecem disponíveis; celulares e tablets recebem uma indicação de que o app é para computadores.

```sh
python3 build.py
python3 -m unittest -v
node --test tests/downloads.test.mjs
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```

Publicado na Cloudflare Pages Free em https://plervo.com, também disponível em https://www.plervo.com e https://plervo-site.pages.dev, usando Direct Upload do diretório `dist`. O domínio permanece registrado na GoDaddy e o DNS está na Cloudflare; ambos os domínios próprios foram verificados por HTTPS. O workflow `Plervo site checks` verifica a geração, os links, a proteção dos downloads e a sugestão de sistema em cada push e pull request. A branch `main` exige PR e esse check aprovado, inclusive para administradores.

A página `/security/` (e suas traduções) aponta para o canal privado de relatos habilitado em `alportblu/plervo-pdf`, no GitHub. O site não recebe o conteúdo desses relatos.

`config.json` controla os links públicos. O apoio está configurado para `https://buymeacoffee.com/alport`, fornecido pelo proprietário e conferido no Chrome oficial em 14 de outubro de 2026: Ricardo Bonetti, criador do Plervo. A página `/support/` (e suas traduções) abre o serviço somente quando o visitante escolhe o link. O download principal é **Plervo Suite 0.1.0-alpha.2** para Mac com Apple Silicon. O usuário instala a Suite e escolhe Plervo PDF pelo catálogo. O instalador da Suite foi assinado, notarizado, examinado e instalado localmente a partir do DMG; não é uma versão estável. Instalação em máquina limpa e cobertura de mais dispositivos seguem pendentes. Windows aguarda assinatura SignPath e validação nativa da Suite. A Suite Linux alpha.3 está publicada, com DEB e RPM validados nas distribuições listadas no site. Publicar o site somente depois que a release correspondente estiver acessível anonimamente. Nunca cadastrar links de exemplo, pacotes sem validação ou uma versão estável inexistente. O gerador exige hash SHA-256, URL no repositório oficial, validação explícita e assinatura para Mac/Windows; Mac também exige notarização. Um pacote PDF direto, ou com versão/plataforma diferente, é recusado como download principal.

Não existem dados bancários, tokens de serviço ou chaves privadas neste projeto.

Identidade SVG, layout e captura da Suite: originais do Plervo. Inter Regular e SemiBold são servidas localmente sob OFL-1.1, com a licença incluída; têm origem nos assets já atribuídos do Plervo PDF. Nenhum recurso gráfico da Adobe ou ArtCraft. A direção visual e as ferramentas pesquisadas estão em `DESIGN.md`.

O endereço `/` é sempre inglês, sem redirecionamento automático por idioma do navegador. O seletor no cabeçalho abre a mesma página em inglês, português (`/pt/`) ou espanhol (`/es/`). A navegação mantém o idioma pelo endereço, sem cookies, armazenamento local ou JavaScript adicional. Páginas de apoio, segurança, privacidade, créditos e 404 têm traduções; os antigos caminhos em português redirecionam para `/pt/`. Metadados, canonical, hreflang e sitemap acompanham cada idioma. Textos ficam em `locales/{en,pt,es}.json`, com paridade de chaves obrigatória. A sugestão de download identifica somente o sistema; não presume a arquitetura do processador e não inicia downloads.

## Catálogo da família

A página inclui Photo, Vector, Video, Develop, Motion, Publish, Write, Slides, Sheets, CAD, Audio e Canvas, com descrições em inglês, português e espanhol. Os ícones são os originais atribuídos da família Plervo; fontes, hashes e licenças ficam em `public/assets/products/`.

A disponibilidade de cada app vem do campo `products` de cada download qualificado em `config.json`. Releases anteriores sem o campo oferecem somente PDF. DEB e RPM da mesma versão devem listar os mesmos produtos. Não acrescentar um produto antes de publicar e verificar seu pacote e o gerenciamento pela Suite naquela plataforma. Enquanto isso, o cartão mostra “Em validação”, sem link que prometa instalação. Slides e Audio indicam a interface em inglês.
