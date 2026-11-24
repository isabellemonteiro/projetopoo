import os

ARQUIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ranking.txt")
MAXIMO_REGISTROS = 10    
TAMANHO_NOME = 12       


class Ranking:
    def __init__(self, arquivo=ARQUIVO):
        self.arquivo = arquivo
        self.registros = []       
        self.carregar()

    @staticmethod
    def _chave(registro):
        return (-registro["pontos"], registro["tempo"])

    def carregar(self):
        self.registros = []
        try:
            with open(self.arquivo, "r", encoding="utf-8") as arquivo:
                linhas = arquivo.read().splitlines()
        except OSError:
            return                                 
        for linha in linhas:
            partes = linha.split(";", 2)
            if len(partes) != 3:
                continue                          
            try:
                self.registros.append({"nome": partes[2][:TAMANHO_NOME],
                                       "pontos": int(partes[0]),
                                       "tempo": int(partes[1])})
            except ValueError:
                continue
        self.registros.sort(key=self._chave)

    def salvar(self):
        try:
            with open(self.arquivo, "w", encoding="utf-8") as arquivo:
                for r in self.registros:
                    arquivo.write(f"{r['pontos']};{r['tempo']};{r['nome']}\n")
        except OSError:
            pass    

    def adicionar(self, nome, pontos, tempo):
        nome = (nome or "").replace(";", " ").replace("\r", " ").replace("\n", " ").strip()[:TAMANHO_NOME] or "JOGADOR"
        novo = {"nome": nome, "pontos": int(pontos), "tempo": int(tempo)}
        self.registros.append(novo)
        self.registros.sort(key=self._chave)         
        self.registros = self.registros[:MAXIMO_REGISTROS]
        self.salvar()
        for i, r in enumerate(self.registros):
            if r is novo:
                return i + 1
        return None

    def melhores(self):
        return list(self.registros)

    @staticmethod
    def formatar_tempo(segundos):
        return f"{segundos // 60:02d}:{segundos % 60:02d}"
