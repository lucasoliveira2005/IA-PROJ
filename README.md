
TODO:
- implementar o A*
- implementar o beam search
- fazer o GUI
- fazer o README real do projeto
- fazer os slides da apresentação

IMPLEMENTED:
- randomness no greedy
- apresentar o score, seja o score do run ou com estatisticas (dependendo da opção escolhida)
- menu simples para escolher mais facilmente os files e modo de execução (com progresso de em que run está)
- integrar o greedy search antigo com randomness (basicamente irrelevante) para mostrar que é pior mas funciona com um tempo somewhat ok para todos os data sets
- run time tracker para podermos comparar run time entre algoritmos
- informação sobre "Score per ride" para poder comprar melhore entre algoritmos
- informação sobre score normalizado para poder comprar eficácia entre data sets (o q o professor tinha pedido)
- menu já modificado para poder escolher entre o greedy normal, o antigo, A* search e Beam search (mesmo q estes ainda n estejam implementados)
- (por enquanto, safe exit para quando o algoritmo ainda não está implementado - vai ser preciso remover depois) <-------------------
- aviso adicionado com o uso da variável heavy_file para quando o A* search ou o Beam search possam ser bastante pesados com o data set escolhido
- comentários adicionados e ligeiramente melhorados para compreensão do código e das suas diferentes secções


COMANDOS:
-pip install flask
-python project1_IA.py
