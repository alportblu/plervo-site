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

`config.json` controla os links públicos. O apoio está configurado para `https://buymeacoffee.com/alport`, fornecido pelo proprietário. O crédito público usa **AlporT**. A página `/support/` (e suas traduções) abre o serviço somente quando o visitante escolhe o link.

O download principal é **Plervo Suite 0.1.0-alpha.4**, para Mac com Apple Silicon ou Linux x86_64. O usuário instala a Suite e escolhe os apps no catálogo. A release oferece PDF, Photo, Vector, Video, Develop, Motion, Publish, Write, Slides, Sheets e CAD nas duas plataformas. Audio e Canvas permanecem em validação. Mac usa pacotes assinados e notarizados; Linux oferece DEB e RPM e exige glibc 2.39 ou superior. As dependências declaradas no pacote da Suite incluem ALSA para os apps multimídia. Windows aguarda confirmação da SignPath e integração da assinatura.

Os downloads públicos dos apps passam por instalação e reinstalação usando os componentes reais da Suite em destinos isolados; Linux também verifica remoção e preservação de arquivos sintéticos. Os testes locais de Linux usam containers x86_64 emulados, além da aceitação nativa registrada no CI. A alpha não é uma versão estável: GUI final e instalação em Mac limpo, hardware de áudio, plugins externos e mais dispositivos continuam fora da cobertura concluída. Consulte as notas da release para os limites atuais.

Publicar o site somente depois que a release correspondente estiver acessível anonimamente e o gerenciamento de cada app anunciado tiver sido verificado pela Suite. Nunca cadastrar links de exemplo, pacotes sem validação ou uma versão estável inexistente. O gerador exige hash SHA-256, URL no repositório oficial, validação explícita e assinatura para Mac/Windows; Mac também exige notarização. Um pacote PDF direto, ou com versão/plataforma diferente, é recusado como download principal.

Não existem dados bancários, tokens de serviço ou chaves privadas neste projeto.

Identidade SVG, layout e captura da Suite: originais do Plervo. A imagem atual mostra a Suite alpha.4 em execução nativa no Ubuntu 24.04, capturada pelo [CI de aceitação](https://github.com/alportblu/plervo-pdf/actions/runs/39001993059), fonte `4da05339d4f6f6715d09f0622975b8164be7f480`. Inter Regular e SemiBold são servidas localmente sob OFL-1.1, com a licença incluída; têm origem nos assets já atribuídos do Plervo PDF. Nenhum recurso gráfico da Adobe ou ArtCraft. A direção visual e as ferramentas pesquisadas estão em `DESIGN.md`.

O endereço `/` é sempre inglês, sem redirecionamento automático por idioma do navegador. O seletor no cabeçalho abre a mesma página em inglês, português (`/pt/`) ou espanhol (`/es/`). A navegação mantém o idioma pelo endereço, sem cookies, armazenamento local ou JavaScript adicional. Páginas de apoio, segurança, privacidade, créditos e 404 têm traduções; os antigos caminhos em português redirecionam para `/pt/`. Metadados, canonical, hreflang e sitemap acompanham cada idioma. Textos ficam em `locales/{en,pt,es}.json`, com paridade de chaves obrigatória. A sugestão de download identifica somente o sistema; não presume a arquitetura do processador e não inicia downloads.

## Catálogo da família

A página inclui Photo, Vector, Video, Develop, Motion, Publish, Write, Slides, Sheets, CAD, Audio e Canvas, com descrições em inglês, português e espanhol. Os ícones são os originais atribuídos da família Plervo; fontes, hashes e licenças ficam em `public/assets/products/`.

A disponibilidade de cada app vem do campo `products` de cada download qualificado em `config.json`. Releases anteriores sem o campo oferecem somente PDF. DEB e RPM da mesma versão devem listar os mesmos produtos. Não acrescentar um produto antes de publicar e verificar seu pacote e o gerenciamento pela Suite naquela plataforma. Enquanto isso, o cartão mostra “Em validação”, sem link que prometa instalação. Slides e Audio indicam a interface em inglês.
