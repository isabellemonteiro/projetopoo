# projetopoo
  Documento de Design: Spirit: Escape from the Castle
1. Título do Jogo
Spirit: escape from the castle
2. Descrição Geral
Tipo: Plataforma 2D com elementos de ação.
Ambiente: Castelo sombrio e cheio de mistérios, dividida entre o plano espiritual e o físico.
Ideia Principal: O jogador alterna na forma de um fantasma e a forma humana para superar obstáculos e derrotar um guardião gigante que protege a saída.
3. Objetivo do Jogo
Atravessar os obstáculos, coletar fragmentos e derrotar o Guardião Scorpion  para escapar do castelo.
4. Personagem Principal
Identidade: Spirit, uma alma que busca fugir de onde foi presa.
Atributos: 3 Chamas de Vida.
Formas:
Fantasma (Padrão): Pulo alto, queda lenta e atravessa certos obstáculos.
Humano: Movimentação pesada, queda rápida e causa dano em pontos fracos.
5. Inimigos e Obstáculos
Esqueletos e Morcegos: Inimigos básicos que patrulham o mapa.
Obstáculos de Cenário: abismos, caixões, etc (dano instantâneo).
O CHEFE FINAL (Scorpion): Uma entidade gigante.
Ataques: Esmagamento com as mãos, sopro de vento.
Ponto Fraco: Um cristal no peito que só pode ser quebrado por um impacto físico.
6. Cenário (Mapa)
Ambiente: Masmorras de pedra com iluminação azulada e roxa.
Estrutura: O mapa começa com plataformas simples e progride ao decorrer do jogo.
Elementos: plataformas móveis e o "Grande Espelho" (o portal para o combate final).
7. Sistema de Pontuação
Cristais de Alma: 20 pontos cada.
Relíquias de Ouro: 50  pontos 
8. Sistema de Vida
Quantidade: 3 corações (Chamas).
Perda de Vida: Ao tocar inimigos, ser atingido pelo chefe ou cair em abismos.
Recuperação: Itens raros, recuperam 1 coração.
Derrota: Se os 3 corações se apagarem, o jogador volta ao início do jogo.
9. Controles
Setas Laterais: Movimentação.
Espaço: Pulo.
10. Fluxo do Jogo
Transição: O jogador encontra o espelho secreto e descobre que vira humano.
O Confronto Final: * O fantasma vira humano e enfrenta o chefe.
Vitória: Após 5 acertos, o chefa cai e o portal de saída se abre.
11. Regras do Jogo
O personagem morre instantaneamente se cair fora dos limites do mapa (buracos).
Após levar dano, o personagem pisca por 1 segundo. Durante esse tempo, ele fica imune a novos ataques, permitindo que o jogador se reposicione. 
Pular sobre o inimigo o elimina.
12. Estrutura do Projeto
engine.py: Gerencia a tela e o loop principal.
player.py: Lógica das duas formas, física e animações.
boss.py: Chefe e seus padrões de ataque.
levels.py: Configuração dos blocos e posição dos itens.
13. Funcionalidades Mínimas 
Movimentação e colisões.
Sistema de troca de forma .
Condições de vitória (matar o boss) e derrota (perder as vidas).
14. Melhorias Futuras
Adicionar um sistema de "Combo" para pontos
Efeitos de luz dinâmica nas tochas do castelo
Adicionar áudio
