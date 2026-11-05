"""Extrae el texto de un bloque HTML identificado por su clase."""

from html.parser import HTMLParser

SALTOS = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li"}
IGNORADOS = {"script", "style", "noscript", "figure", "figcaption", "aside", "nav", "form"}


class _Bloque(HTMLParser):
    def __init__(self, clase):
        super().__init__(convert_charrefs=True)
        self.clase = clase
        self.etiqueta = None
        self.profundidad = 0
        self.ignorando = 0
        self.terminado = False
        self.partes = []

    def handle_starttag(self, tag, attrs):
        if self.terminado:
            return
        if self.etiqueta is None:
            atributos = dict(attrs)
            if self.clase in (atributos.get("class") or "").split() or atributos.get("id") == self.clase:
                self.etiqueta, self.profundidad = tag, 1
            return
        if tag == self.etiqueta:
            self.profundidad += 1
        if tag in IGNORADOS:
            self.ignorando += 1

    def handle_endtag(self, tag):
        if self.etiqueta is None or self.terminado:
            return
        if tag in IGNORADOS and self.ignorando:
            self.ignorando -= 1
        if tag in SALTOS:
            self.partes.append("\n")
        if tag == self.etiqueta:
            self.profundidad -= 1
            self.terminado = self.profundidad == 0

    def handle_data(self, data):
        if self.etiqueta and not self.terminado and not self.ignorando:
            self.partes.append(data)


def texto_de_bloque(pagina, clase):
    lector = _Bloque(clase)
    lector.feed(pagina)
    lineas = (" ".join(linea.split()) for linea in "".join(lector.partes).split("\n"))
    return "\n".join(linea for linea in lineas if linea)


if __name__ == "__main__":
    prueba = (
        '<div class="otro">no</div><div class="post-cuerpo x"><p>Uno <b>dos</b></p>'
        "<div><p>Tres &amp; cuatro</p></div><script>no()</script><figure>no</figure></div><p>fuera</p>"
    )
    assert texto_de_bloque(prueba, "post-cuerpo") == "Uno dos\nTres & cuatro"
    assert texto_de_bloque(prueba, "falta") == ""
    assert texto_de_bloque('<div id="cuerpo"><p>Hola</p></div>', "cuerpo") == "Hola"
    print("selfcheck ok")
