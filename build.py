"""Build the static site with local-only download suggestions and no remote widgets."""
import html
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent


def checked_url(value, host):
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or parsed.netloc != host
            or parsed.query or parsed.fragment or not parsed.path.strip("/")
            or re.search(r"[\s<>\\]", value)):
        raise ValueError(f"Expected a public HTTPS URL on {host}")
    return html.escape(value, quote=True)


def render(template, values):
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    if re.search(r"\{\{[A-Z_]+\}\}", template):
        raise ValueError("Unfilled template")
    return template


def main():
    config = json.loads((ROOT / "config.json").read_text())
    if config["site_url"] != "https://plervo.com":
        raise ValueError("Unexpected production domain")
    donation = config["buy_me_a_coffee_url"]
    if donation:
        donation = checked_url(donation, "buymeacoffee.com")
    source = config["source_url"]
    if source:
        source = checked_url(source, "github.com")
    platforms = {"windows": ("Windows", "Instalador MSI"), "macos": ("macOS", "Pacote DMG"), "linux": ("Linux", "Pacotes para Linux")}
    downloads = {}
    for release in config["downloads"]:
        platform = release["platform"]
        if platform not in platforms or platform in downloads:
            raise ValueError("Unknown or duplicate platform")
        url = checked_url(release["url"], "github.com")
        if not urlsplit(release["url"]).path.startswith("/alportblu/plervo-pdf/releases/download/"):
            raise ValueError("Installer must come from the Plervo release repository")
        if not re.fullmatch(r"[a-f0-9]{64}", release["sha256"]):
            raise ValueError("Installer SHA-256 is required")
        if release.get("validated") is not True:
            raise ValueError("Do not publish an unvalidated installer")
        downloads[platform] = (url, release)
    dest = ROOT / "dist"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(ROOT / "public", dest)
    cards = []
    for platform, (label, format_name) in platforms.items():
        action = '<span class="pending">Em validação interna</span>'
        if platform in downloads:
            url, release = downloads[platform]
            checksum = f"plervo-pdf-{platform}.sha256"
            (dest / checksum).write_text(release["sha256"] + "  " + urlsplit(release["url"]).path.rsplit("/", 1)[-1] + "\n")
            action = f'<a class="button" href="{url}">Baixar {html.escape(release["version"])} ↗</a><a class="hash" href="/{checksum}">Verificar SHA-256</a>'
        cards.append(f'<article class="download" id="download-{platform}" data-platform="{platform}"><h3>{label}</h3><p>{format_name}</p>{action}</article>')
    home = render((ROOT / "templates/index.html").read_text(), {"DOWNLOADS": "".join(cards)})
    if donation:
        home = home.replace("Estamos preparando nossa página no Buy Me a Coffee.", "Você pode contribuir pelo Buy Me a Coffee.")
    (dest / "index.html").write_text(home)
    support_action = '<div class="notice"><strong>Nosso café ainda está passando.</strong><p>A página oficial de apoio está sendo preparada. Assim que estiver disponível, o link aparecerá aqui.</p></div>'
    if donation:
        support_action = f'<p><a class="button" href="{donation}" rel="noopener noreferrer">Apoiar pelo Buy Me a Coffee ↗</a></p>'
    pages = {
        "apoiar": ("Apoie o próximo passo.", "Apoio voluntário ao desenvolvimento do Plervo.", '<p>O Plervo nasce para tornar o trabalho com documentos mais acessível. Seu apoio ajuda com desenvolvimento, testes, distribuição e manutenção.</p>' + support_action + '<h2>Uma contribuição, por escolha sua.</h2><p>O apoio é voluntário e não desbloqueia recursos do aplicativo. O pagamento acontece no Buy Me a Coffee: o Plervo não recebe nem armazena os dados do seu cartão.</p><p>Você só abre o serviço de pagamento quando escolhe seguir o link. Não carregamos widgets ou rastreadores dele neste site.</p>'),
        "seguranca": ("Segurança é trabalho contínuo.", "Como o Plervo prepara suas versões e trata segurança.", '<p>Estamos preparando a primeira versão do Plervo PDF. Ainda não há uma versão pública validada para uso em produção.</p><h2>O que estamos verificando</h2><ul><li>Origem do código, licenças e dependências.</li><li>Limites da automação local e autenticação por sessão.</li><li>Abertura de arquivos inválidos e preservação dos documentos.</li><li>Identidade, integridade e instalação dos pacotes de cada sistema.</li></ul><h2>Publicação com evidências</h2><p>Quando houver uma versão disponível, esta página apontará para os arquivos oficiais, notas da versão e seus resumos SHA-256. Um hash verifica integridade; a assinatura do pacote ajuda a verificar sua origem.</p><h2>Limites claros</h2><p>Nenhuma auditoria garante ausência de falhas. A compatibilidade com todos os PDFs e recursos de outros editores não é garantida. Use cópias dos documentos durante a fase de testes.</p><h2>Relatar uma possível falha</h2><p>Use o <a href="https://github.com/alportblu/plervo-pdf/security" rel="noopener noreferrer">canal privado de segurança no GitHub</a> e escolha “Report a vulnerability”. Inclua a versão, o sistema e os passos para reproduzir com um documento de teste. Não publique senhas ou documentos pessoais em issues públicas.</p>'),
        "privacidade": ("Seus documentos são seus.", "Privacidade no site do Plervo e no aplicativo em preparação.", '<h2>Este site</h2><p>Este site não usa cookies de publicidade, analytics, formulários ou envio de PDFs. Seu provedor de hospedagem pode processar informações técnicas da conexão, como endereço IP, para entregar e proteger as páginas.</p><h2>Sugestão de download</h2><p>O navegador sugere um sistema para facilitar a escolha do instalador. Essa identificação acontece no seu dispositivo, sem armazenar ou enviar essas informações. Você pode escolher outro sistema.</p><h2>O aplicativo</h2><p>A base do Plervo PDF processa documentos no próprio computador. A primeira versão está em desenvolvimento; publicaremos aqui a descrição dos recursos de rede efetivamente incluídos antes de disponibilizar os instaladores.</p><h2>Links externos</h2><p>Downloads levarão ao GitHub. Ao escolher o link de apoio voluntário, você acessa a página de Ricardo Bonetti, criador do Plervo, no Buy Me a Coffee. Ao visitar esses serviços, aplicam-se as políticas de privacidade deles.</p><p>Atualizado em 14 de outubro de 2026.</p>'),
        "sobre": ("Uma marca própria. Uma base aberta.", "Origem, autoria e créditos do Plervo PDF.", '<p>Plervo é uma iniciativa independente. Começamos pelo Plervo PDF, baseado na versão 0.8.0 do projeto <a href="https://github.com/storytold/pdfcraft" rel="noopener noreferrer">PdfCraft</a>, com identidade própria e trabalho de revisão e segurança.</p><p>Preservamos os créditos dos autores e as licenças MIT e Apache-2.0 da base. Bibliotecas, ícones e fontes mantêm suas próprias licenças, incluídas nos pacotes.</p><h2>Transparência desde o início</h2><p>O aplicativo ainda está em desenvolvimento. A disponibilidade de recursos e os sistemas suportados serão descritos nas notas de cada versão testada.</p>' + (f'<p><a href="{source}" rel="noopener noreferrer">Código-fonte do Plervo PDF ↗</a></p>' if source else '<p>O endereço do código-fonte do Plervo será publicado junto da primeira versão.</p>') + '<p>Plervo não é afiliado à Adobe nem à equipe ArtCraft. Adobe e Acrobat são marcas de seus respectivos titulares.</p>'),
    }
    template = (ROOT / "templates/page.html").read_text()
    for slug, (title, description, content) in pages.items():
        (dest / slug).mkdir()
        (dest / slug / "index.html").write_text(render(template, {"TITLE": html.escape(title), "DESCRIPTION": html.escape(description), "SLUG": slug, "CONTENT": content}))
    sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>https://plervo.com/{slug}</loc></url>' for slug in ["", *(s + "/" for s in pages)]) + '</urlset>\n'
    (dest / "sitemap.xml").write_text(sitemap)
    (dest / "404.html").write_text(render(template, {"TITLE": "Esta página não está aqui.", "DESCRIPTION": "Página não encontrada.", "SLUG": "404", "CONTENT": '<p>Volte ao início para conhecer o Plervo PDF.</p><a class="button" href="/">Voltar ao início</a>'}))
    print(f"Site gerado: {dest}")


if __name__ == "__main__":
    main()
