# StationPlaylist #
* Authors: Christopher Duffley <nvda@chrisduffley.com> (formerly Joseph Lee
  <joseph.lee22590@gmail.com>, originally by Geoff Shang and other
  contributors)
* Baixe a [versão estável][1]
* NVDA compatibility: 2022.4 and later

Este pacote de complemento fornece uso aprimorado do StationPlaylist Studio
e outros aplicativos StationPlaylist, além de fornecer utilitários para
controlar o Studio de qualquer lugar. Os aplicativos compatíveis incluem
Studio, Creator — Criador —, Track Tool — Ferramenta de Faixa —, VT Recorder
e Streamer, bem como codificadores — encoders — SAM, SPL e AltaCast.

Para obter mais informações sobre o complemento, leia o [guia do
complemento][2].

NOTAS IMPORTANTES:

* This add-on requires StationPlaylist suite 5.40 or later.
* Some add-on features will be disabled or limited if NVDA is running in
  secure mode such as in logon screen.
* For best experience, disable audio ducking mode.
* Starting from 2018, [changelogs for old add-on releases][3] will be found
  on GitHub. This add-on readme will list changes from version 23.02 (2023)
  onwards.
* Enquanto o Studio está em execução, você pode salvar, recarregar as
  configurações salvas ou redefinir as configurações do complemento para os
  padrões pressionando Control+NVDA+C, Control+NVDA+R uma vez ou
  Control+NVDA+R três vezes, respectivamente. Isso também se aplica às
  configurações do codificador - você pode salvar e redefinir (não
  recarregar) as configurações do codificador se estiver usando
  codificadores.

## Teclas de atalho

A maioria delas funcionará no Studio apenas a menos que seja especificado de
outra forma.

* Alt+Shift+T na janela do Studio: anuncia o tempo decorrido para a faixa
  atualmente em reprodução.
* Control+Alt+T (deslizar dois dedos para baixo no modo tátil SPL) na janela
  do Studio: anuncia o tempo restante para a faixa atualmente em reprodução.
* NVDA+Shift+F12 (deslizar com dois dedos para cima no modo tátil SPL) na
  janela do Studio: anuncia o tempo da emissora como 5 minutos para o início
  da hora. Pressionar este comando duas vezes anunciará os minutos e
  segundos até o início da hora.
* Alt+NVDA+1 (deslizar com dois dedos para a direita no modo tátil SPL) na
  janela do Studio: Abre a categoria de alarmes na caixa de diálogo de
  configuração do complemento do Studio.
* Alt+NVDA+1 no Editor de Lista de Reprodução do Creator e no editor de
  lista de reprodução Remote VT: Anuncia a hora programada para a lista de
  reprodução — playlist — carregada.
* Alt+NVDA+2 no Editor de Lista de Reprodução do Creator e editor de lista
  de reprodução Remote VT: Anuncia a duração total da lista de reprodução.
* Alt+NVDA+3 na janela do Studio: Alterna o explorador do carrinho — cart —
  para aprender as atribuições de carrinho.
* Alt+NVDA+3 no Editor de Lista de Reprodução do Creator e editor de lista
  de reprodução Remote VT: Anuncia quando a faixa selecionada está
  programada para tocar.
* Alt+NVDA+4 no Editor de Lista de Reprodução do Creator e editor de lista
  de reprodução Remote VT: Anuncia rotação e categoria associada à lista de
  reprodução carregada.
* Control+NVDA+f na janela do Studio: Abre um diálogo para localizar uma
  faixa baseada no intérprete ou nome da música. Pressione NVDA+F3 para
  localizar para frente ou NVDA+Shift+F3 para localizar para trás.
* Alt+NVDA+R na janela do Studio: Passa pelas configurações de anúncio de
  varredura — scan — da biblioteca.
* Control+Shift+X na janela do Studio: Passa pelas configurações do
  temporizador braille.
* Control+Alt+seta para esquerda/direita (enquanto focalizado numa faixa no
  Studio, Creator, Remote VT e Ferramenta de Faixa): Move-se para a coluna
  anterior/seguinte da faixa.
* Control+Alt+seta para cima/baixo (enquanto focalizado numa faixa no
  Studio, Creator, Remote VT e ferramenta de Faixa): Move-se para a faixa
  anterior/seguinte e anuncia colunas específicas.
* Control+NVDA+1 a 0 (enquanto focalizado numa faixa no Studio, Creator
  (incluindo o Editor de Lista de Reprodução), Remote VT e ferramenta de
  Faixa): Anuncia o conteúdo da coluna para uma coluna especificada (as
  primeiras dez colunas por padrão). Pressionar este comando duas vezes
  exibirá as informações da coluna numa janela em modo de navegação.
* Control+NVDA+- (hífen enquanto focalizado numa faixa no Studio, Creator,
  Remote VT e Ferramenta de Faixa): exibe dados para todas as colunas numa
  trilha em uma janela do modo de navegação.
* NVDA+V enquanto focalizado numa faixa (somente visualizador de lista de
  reprodução do Studio): alterna o anúncio da coluna da faixa entre a ordem
  da tela e a ordem personalizada.
* Alt+NVDA+C enquanto focalizado numa faixa (somente visualizador da lista
  de reprodução do Studio): anuncia os comentários da faixa, se houver.
* Alt+NVDA+0 na janela do Studio: Abre o diálogo de configuração do
  complemento do Studio.
* Alt+NVDA+P na janela do Studio: abre o diálogo de perfis de transmissão —
  broadcast — do Studio.
* Alt+NVDA+F1: abre o diálogo de boas-vindas.

## Comandos não atribuídos

Os comandos a seguir não são atribuídos por padrão; se desejar atribuí-los,
use o diálogo Definir comandos — Gestos de entrada — para adicionar comandos
personalizados. Para fazer isso, na janela do Studio, abra o menu NVDA,
Preferências e Definir comandos. Expanda a categoria StationPlaylist,
localize os comandos não atribuídos na lista abaixo e selecione "Adicionar"
e digite o comando — gesto — que deseja usar.

Important: some of these commands will not work if NVDA is running in secure
mode such as from login screen.

* Switching to SPL Studio window from any program (unavailable in secure
  mode).
* SPL Controller layer (unavailable in secure mode).
* Announcing Studio status such as track playback from other programs
  (unavailable in secure mode).
* Announcing encoder connection status from any program (unavailable in
  secure mode).
* Camada Assistente SPL do SPL Studio.
* Anuncia o tempo incluindo segundos, do SPL Studio.
* Anúncio da temperatura.
* Anúncio do título da próxima faixa, se programada.
* Anúncio do título da faixa atualmente em reprodução.
* Marcando a faixa atual para o início da análise do tempo da faixa.
* Executando análise de tempo da faixa.
* Tira instantâneos — snapshots — da lista de reprodução.
* Localiza texto em colunas específicas.
* Localiza faixas com duração dentro de um determinado intervalo por meio do
  localizador de intervalo de tempo.
* Habilita ou desabilita o fluxo — streaming — de metadados rapidamente.

## Comandos adicionais ao usar codificadores

Os seguintes comandos estão disponíveis ao usar codificadores — encoders:

* F9: conecte o codificador selecionado.
* F10 (somente codificador SAM): Desconecte o codificador selecionado.
* Control+F9: Conecte todos os codificadores.
* Control+F10 (somente codificador SAM): Desconecte todos os codificadores.
* Control+Shift+F11: Toggles whether NVDA will switch to Studio window for
  the selected encoder if connected.
* Shift+F11: Define se o Studio reproduzirá a primeira faixa selecionada
  quando o codificador estiver conectado a um servidor de fluxo — streaming.
* Control+F11: Alterna o monitoramento em segundo plano do codificador
  selecionado.
* Control+F12: abre um diálogo para selecionar o codificador que você
  excluiu (para realinhar os rótulos e as configurações do codificador).
* Alt+NVDA+0 e F12: Abre o diálogo de configurações do codificador para
  configurar opções como o rótulo do codificador.

Além disso, comandos de revisão/exploração de coluna estão disponíveis,
incluindo:

* Control+NVDA+1: Posição do codificador.
* Control+NVDA+2: rótulo do codificador.
* Control+NVDA+3 no codificador SAM: formato do codificador.
* Control+NVDA+3 no SPL e no Codificador AltaCast: Configurações do
  codificador.
* Control+NVDA+4 no codificador SAM: Status de conexão do codificador.
* Control+NVDA+4 no SPL e no Codificador AltaCast: Taxa de transferência ou
  status da conexão.
* Control+NVDA+5 no codificador SAM: descrição do status da conexão.

## Camada Assistente SPL

Este conjunto de comandos de camada permite obter vários status no SPL
Studio, como se uma faixa está sendo reproduzida, duração total de todas as
faixas durante a hora e assim por diante. Em qualquer janela do SPL Studio,
pressione o comando da camada Assistente SPL e, em seguida, pressione uma
das teclas da lista abaixo (um ou mais comandos são exclusivos do
visualizador da lista de reprodução). Você também pode configurar o NVDA
para emular comandos de outros leitores de tela.

Os comandos disponíveis são:

* A: Automatização.
* C (Shift+C no leiaute JAWS): Título para a faixa atualmente em reprodução.
* C (leiaute JAWS): Alternar explorador de carrinho (somente visualizador de
  lista de reprodução).
* D (R no leiaute JAWS): Duração restante para a lista de reprodução (se uma
  mensagem de erro for dada, mova para o visualizador da lista de reprodução
  e, em seguida, execute este comando).
* E: Status de fluxo de metadados.
* Shift+1 a Shift+4, Shift+0: status para URLs de fluxo — streaming — de
  metadados individuais (0 é para codificador DSP).
* F: Localizar faixa (somente visualizador da lista de reprodução).
* H: Duração da música para a hora de programação.
* Shift+H: duração restante da faixa para a hora de programação.
* I (L no leiaute JAWS): Contagem de ouvintes.
* K: Mova para a faixa marcada (somente visualizador da lista de
  reprodução).
* Control+K: Defina a faixa atual como a faixa do marcador de lugar (somente
  visualizador de lista de reprodução).
* L (Shift+L no leiaute JAWS): Entrada de linha.
* M: Microfone.
* N: Título para a próxima faixa programada.
* P: Status de reprodução (reproduzindo ou parado).
* Shift+P: Tonalidade — pitch — da faixa atual.
* * R (Shift+E no leiaute JAWS): Gravar no arquivo habilitado/desabilitado.
* Shift+R: Monitora a varredura da biblioteca em andamento.
* S: A faixa começa (programada).
* Shift+S: tempo até que a faixa selecionada seja reproduzida (a faixa
  começa em).
* T: Modo de edição/inserção do carrinho ativado/desativado.
* U: Tempo em atividade do Studio.
* W: Clima e temperatura, se configurados.
* Y: Status modificado da lista de reprodução.
* F8: Tire instantâneos da lista de reprodução (número de faixas, faixa mais
  longa, etc.).
* Shift+F8: Solicita transcrições da lista de reprodução em vários formatos.
* F9: Marca a faixa atual para o início da análise da lista de reprodução
  (somente visualizador da lista de reprodução).
* F10: Executa a análise de tempo da faixa (somente visualizador da lista de
  reprodução).
* F12: Alternar entre o perfil atual e um predefinido.
* F1: Ajuda da camada.

## Controlador SPL

O Controlador SPL é um conjunto de comandos em camadas que você pode usar
para controlar o SPL Studio de qualquer lugar. Pressione o comando da camada
Controlador SPL e o NVDA dirá, "Controlador SPL". Pressione outro comando
para controlar várias configurações do Studio, como ligar/desligar o
microfone ou reproduzir a próxima faixa.

Important: SPL Controller layer commands are disabled if NVDA is running in
secure mode.

Os comandos do Controlador SPL disponíveis são:

* P: reproduz a próxima faixa selecionada.
* U: pausa ou retoma a reprodução.
* S: Para a faixa com enfraquecimento — fade out.
* T: Parada instantânea.
* M: Liga o microfone.
* Shift+M: Desliga o microfone.
* A: Ativa a automatização.
* Shift+A: Desativa a automatização.
* L: Ativa entrada de linha.
* Shift+L: Desativa a entrada de linha.
* R: Tempo restante para a faixa atualmente em reprodução.
* Shift+R: Progresso da varredura da biblioteca.
* C: Título e duração da faixa atualmente em reprodução.
* Shift+C: Título e duração da próxima faixa, se houver.
* E: Status de conexão do codificador.
* I: Contagem de ouvintes.
* Q: Informações de status do Studio, como se uma faixa está sendo
  reproduzida, se o microfone está ativado e outros.
* Teclas do carrinho (F1, Control+1, por exemplo): Reproduz carrinhos
  atribuídos de qualquer lugar.
* H: Ajuda da camada.

## Alarmes de faixa e microfone

Por padrão, o NVDA irá tocar um bipe se faltarem cinco segundos na faixa
(outro) e/ou introdução, bem como ouvir um bipe se o microfone estiver ativo
por um tempo. Para configurar alarmes de faixa e microfone, pressione
Alt+NVDA+1 para abrir as configurações de alarmes na tela de configurações
do complemento do Studio. Também pode usar essa tela para configurar se
ouvirá um bipe, uma mensagem ou ambos quando os alarmes forem ativados.

## Localizador de Faixa

Se você deseja localizar rapidamente uma música por um intérprete ou pelo
nome da música, na lista de faixas, pressione Control+NVDA+F. Digite ou
escolha o nome do intérprete ou o nome da música. O NVDA irá colocá-lo na
música se for localizada ou exibirá um erro se não puder encontrar a música
que você está procurando. Para localizar uma música ou intérprete digitado
anteriormente, pressione NVDA+F3 ou NVDA+Shift+F3 para localizar pra frente
ou pra trás.

Nota: Localizador de Faixa diferencia maiúsculas de minúsculas.

## Explorador de carrinho

Dependendo da edição, o SPL Studio permite que até 96 carrinhos sejam
atribuídos para reprodução. O NVDA permite que você ouça qual carrinho ou
jingle está atribuído a esses comandos.

Para aprender as atribuições do carrinho, no SPL Studio, pressione
Alt+NVDA+3. Pressionar o comando do carrinho uma vez informará qual jingle
está atribuído ao comando. Pressione o comando do carrinho duas vezes para
reproduzir o jingle. Pressione Alt+NVDA+3 para sair do explorador do
carrinho. Consulte o guia do complemento para obter mais informações sobre o
explorador de carrinho.

## Análise de tempo de faixa

Para obter a duração da reprodução das faixas selecionadas, marque a faixa
atual para o início da análise do tempo da faixa (Assistente SPL, F9) e
pressione Assistente SPL, F10 quando chegar ao final da seleção.

## Explorador de colunas

Pressionando Control+NVDA+1 a 0, você pode obter o conteúdo de colunas
específicas. Por padrão, essas são as primeiras dez colunas para um item de
faixa (no Studio: intérprete, título, duração, introdução, outro, categoria,
ano, álbum, gênero, modo). Para o editor de lista de reprodução no Creator e
cliente Remote VT, os dados da coluna dependem da ordem das colunas,
conforme mostrada na tela. No Studio, lista de faixas principal do Creator,
e Ferramenta de Faixa, os espaços de coluna são predefinidos
independentemente da ordem das colunas na tela e podem ser configurados no
diálogo de configurações do complemento na categoria de explorador de
colunas.

## Anúncio da coluna de faixa

Você pode pedir ao NVDA para anunciar as colunas das faixas encontradas no
visualizador da lista de reprodução do Studio na ordem em que aparecem na
tela ou usando uma ordem personalizada e/ou excluir certas
colunas. Pressione NVDA+V para alternar este comportamento enquanto focaliza
uma faixa no visualizador de lista de reprodução do Studio. Para
personalizar a inclusão e a ordem das colunas, no painel de configurações de
anúncio da coluna nas configurações do complemento, desmarque "Anunciar
colunas na ordem mostrada na tela" e, em seguida, personalize as colunas
incluídas e/ou a ordem das colunas.

## Instantâneos da lista de reprodução

Você pode pressionar Assistente SPL, F8 enquanto estiver focalizado numa
lista de reprodução no Studio para obter várias estatísticas sobre uma
playlist, incluindo o número de faixas na lista de reprodução, a faixa mais
longa, os principais intérpretes e assim por diante. Depois de atribuir um
comando personalizado para este recurso, pressionar o comando personalizado
duas vezes fará com que o NVDA apresente informações instantâneas da lista
de reprodução como uma página web para que você possa usar o modo de
navegação para navegar (pressione Esc para fechar).

## Transcrições da Lista de Reprodução

Pressionando Assistente SPL, Shift+F8 apresentará um diálogo para permitir
que você solicite transcrições da lista de reprodução em vários formatos,
incluindo um formato de texto simples, uma tabela HTML ou uma lista.

## Diálogo de configuração

From studio window, you can press Alt+NVDA+0 to open the add-on
configuration dialog. Alternatively, go to NVDA's preferences menu and
select SPL Studio Settings item. Not all settings are available if NVDA is
running in secure mode.

## Diálogo de perfis de transmissão

Você pode salvar as configurações de programas específicos em perfis de
transmissão — broadcast. Esses perfis podem ser gerenciados por meio do
diálogo de perfis de transmissão SPL, que pode ser acessado pressionando
Alt+NVDA+P na janela do Studio.

## Modo tátil SPL

If you are using Studio on a touchscreen computer with NVDA installed, you
can perform some Studio commands from the touchscreen. First use three
finger tap to switch to SPL mode, then use the touch commands listed above
to perform commands.

## Version 24.01

* The commands for the Encoder Settings dialog for use with the SPL and SAM
  Encoders are now assignable, meaning that you can change them from their
  defaults under the StationPlaylist category in NVDA Menu > Preferences >
  Input Gestures. The ones that are not assignable are the connect and
  disconnect commands. Also, to prevent command conflicts and make much
  easier use of this command on remote servers, the default gesture for
  switching to Studio after connecting is now Control+Shift+F11 (previously
  just F11). All of these can of course still be toggled from the Encoder
  Settings dialog (NVDA+Alt+0 or F12).

## Version 23.05

* To reflect the maintainer change, the manifest has been updated to
  indicate as such.

## Version 23.02

* NVDA 2022.4 or later is required.
* Windows 10 21H2 (November 2021 Update/build 19044) or later is required.
* In Studio's playlist viewer, NVDA will not announce column headers such as
  artist and title if table headers setting is set to either "rows and
  columns" or "columns" in NVDA's document formatting settings panel.

## Versões mais antigas

Please see the [changelog][3] for release notes for old add-on releases.

[[!tag dev stable]]

[1]: https://www.nvaccess.org/addonStore/legacy?file=stationPlaylist

[2]: https://github.com/chrisDuffley/stationplaylist/wiki/SPLAddonGuide

[3]: https://github.com/ChrisDuffley/stationplaylist/wiki/splchangelog
