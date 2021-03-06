# StationPlaylist #

* Auteurs: Geoff Shang, Joseph Lee et d'autres contributeurs.
* Télécharger [version stable][1]
* Télécharger [la version de développement][2]
* NVDA compatibility: 2019.3 and beyond
* Download [older version][6] compatible with NVDA 2019.2.1 and earlier

This add-on package provides improved usage of StationPlaylist Studio and
other StationPlaylist apps, as well as providing utilities to control Studio
from anywhere. Supported apps include Studio, Creator, Track Tool, VT
Recorder, and Streamer, as well as SAM, SPL, and AltaCast encoders.

Pour plus d’informations sur l'extension, lisez le [guide de
l'extension][4]. Pour les développeurs cherchant à savoir comment construire
l'extension, voir buildInstructions.txt situé à la racine du code source du
référentiel de l'extension.

NOTES IMPORTANTES :

* This add-on requires NVDA 2019.3 or later and StationPlaylist suite 5.20
  or later.
* Si vous utilisez Windows 8 ou ultérieur, pour une meilleure expérience,
  désactiver le Mode d'atténuation audio.
* Starting from 2018, [changelogs for old add-on releases][5] will be found
  on GitHub. This add-on readme will list changes from version 17.08 (2017
  onwards).
* Certaines fonctionnalités de l'extension ne fonctionneront pas dans
  certaines conditions, notamment l'exécution de NVDA en mode sécurisé.
* En raison de limitations techniques, vous ne pouvez pas installer ou
  utiliser cette extension sur la version Windows Store de NVDA.
* Les fonctionnalités marquées comme "expérimental" servent à tester quelque
  chose avant une publication plus vaste, elles ne seront donc pas activées
  dans les versions stables.

## Raccourcis clavier

La plupart d'entre eux fonctionneront dans Studio uniquement sauf indication
contraire.

* Alt+Maj+T depuis la fenêtre de Studio : annonce le temps écoulé pour la
  piste en cours de lecture.
* Contrôle+Alt+T (glissement à deux doigts vers le bas en mode tactile SPL)
  depuis la fenêtre de Studio : annoncer le temps restant pour la piste en
  cours de lecture.
* NVDA+Maj+F12 (glissement à deux doigts vers le haut en mode tactile SPL)
  depuis la fenêtre de Studio: annonce le temps de diffusion tel que 5
  minutes en haut de l'heure. Appuyez deux fois sur cette commande pour
  annoncer les minutes et les secondes jusqu'au début de l'heure.
* Alt+NVDA+1 (glissement à deux doigts vers la droite en mode SPL) depuis la
  fenêtre de Studio: Ouvre la boîte de dialogue  paramètre fin de piste.
* Alt+NVDA+2 (glissement à deux doigts vers la gauche en mode tactile SPL)
  depuis la fenêtre de Studio: Ouvre la boîte de dialogue  paramètre alarme
  chanson intro.
* Alt+NVDA+3 depuis la fenêtre de Studio : Basculer l'explorateur de chariot
  pour apprendre les assignations de chariot.
* Alt+NVDA+4 depuis la fenêtre de Studio : Ouvre le dialogue alarme
  microphone.
* Control+NVDA+f from Studio window: Opens a dialog to find a track based on
  artist or song name. Press NVDA+F3 to find forward or NVDA+Shift+F3 to
  find backward.
* Alt+NVDA+R depuis la fenêtre de Studio : parcourt les paramètres d'annonce
  du balayage dans la bibliothèque.
* Contrôle+Maj+X depuis la fenêtre de Studio : Parcourt les paramètres du
  minuteur braille.
* Contrôle+Alt+flèche gauche/droite (alors que  a été mis en focus sur une
  piste dans Studio, Creator, et l'Outil de piste): Annoncer colonne de
  piste précédente/suivante.
* Contrôle+Alt+flèche haut/bas (alors que  a été mis en focus sur une piste
  dans Studio): Déplacer vers la piste précédente ou suivante et annoncer
  des colonnes spécifiques (indisponible dans l'extension 15.x).
* Contrôle+NVDA+1 à 0 (alors que  a été mis en focus sur une piste dans
  Studio, Creator et l'Outil de piste): Annoncer le contenu de la colonne
  pour une colonne spécifiée. Si vous appuyez deux fois sur cette commande,
  les informations de colonne s'affichent dans une fenêtre en mode
  navigation.
* Contrôle+NVDA+- (tiret dans Studio): affiche les données pour toutes les
  colonnes d'une piste dans une fenêtre en mode navigation.
* Alt+NVDA+C alors que  a été mis en focus sur une piste (Studio
  uniquement): annonce les commentaires de piste le cas échéant.
* Alt+NVDA+0 depuis la fenêtre de Studio : Ouvre le dialogue de
  configuration de l'extension Studio.
* Alt+NVDA+- (tiret) depuis la fenêtre de Studio : Envoyez vos commentaires
  au développeur de l'extension en utilisant le client de messagerie par
  défaut.
* Alt+NVDA+F1: Ouvre le dialogue de bienvenue.

## Commandes non assignées

The following commands are not assigned by default; if you wish to assign
them, use Input Gestures dialog to add custom commands. To do so, from
Studio window, open NVDA menu, Preferences, then Input Gestures. Expand
StationPlaylist category, then locate unassigned commands from the list
below and select "Add", then type the gesutre you wish to use.

* Basculement vers la fenêtre SPL Studio depuis n'importe quel programme.
* Couche Contrôleur SPL.
* Annonçant le statut de Studio, comme la lecture de pistes à partir
  d'autres programmes.
* Announcing encoder connection status from any program.
* Couche Assistant SPL depuis SPL Studio.
* Annoncer le temps y compris les secondes depuis SPL Studio.
* Annonce de la température.
* Annonce du titre de la piste suivante si planifié.
* Annonçant le titre de la piste en cours de lecture.
* Marquage de piste en cours pour le début de l'analyse de durée de piste.
* Effectuer des analyses de durée de piste.
* Prendre des instantanés de playlist
* Recherche de texte dans des colonnes spécifiques.
* Trouver des piste avec une durée qui se situe dans un intervalle donné via
  la recherche de l'intervalle de temps.
* Activer ou désactiver les métadonnées en streaming rapidement.

## Additional commands when using encoders

The following commands are available when using encoders:

* F9 : Se connecter à un serveur de streaming.
* F10 (Encodeur SAM uniquement) : Se déconnecter d'un serveur de streaming.
* Contrôle+F9/Contrôle+F10 (encodeur SAM uniquement) : Connecter ou
  déconnecter tous les encodeurs, respectivement.
* F11 : Détermine si NVDA bascule vers la fenêtre Studio pour l'encodeur
  sélectionné  si connecté.
* Maj+F11: Détermine si Studio lit la première piste sélectionnée lorsque
  l'encodeur est connecté à un serveur de streaming.
* Contrôle+F11 : Active ou désactive le contrôle en arrière-plan de
  l'encodeur sélectionné.
* F12 :: Ouvre un dialogue de saisie d'une étiquette personnalisée pour le
  flux ou l'encodeur sélectionné.
* Contrôle+F12 : Ouvre un dialogue pour sélectionner l'encodeur que vous
  avez supprimé (afin de réaligner les étiquettes de flux et les paramètres
  de l'encodeur).
* Alt+NVDA+0 : Ouvre la boîte de dialogue paramètres  de l'encodeur pour
  configurer des options telles que l'étiquette de flux.

De plus, les commandes pour visualiser la colonne sont disponibles, y
compris :

* Contrôle+NVDA+1 : Position de l'encodeur.
* Contrôle+NVDA+2 : étiquette de flux.
* Contrôle+NVDA+3 depuis l'Encodeur SAM : Format de l'Encodeur.
* Control+NVDA+3 from SPL and AltaCast Encoder: Encoder settings.
* Control+NVDA+4 from SAM Encoder: Encoder connection status.
* Control+NVDA+4 from SPL and AltaCast Encoder: Transfer rate or connection
  status.
* Contrôle+NVDA+5 depuis l'Encodeur SAM : Description du statut de la
  connexion.

## Couche Assistant SPL

This layer command set allows you to obtain various status on SPL Studio,
such as whether a track is playing, total duration of all tracks for the
hour and so on. From any SPL Studio window, press the SPL Assistant layer
command, then press one of the keys from the list below (one or more
commands are exclusive to playlist viewer). You can also configure NVDA to
emulate commands from other screen readers.

Les commandes disponibles sont :

* A : Automatisation.
* C (Maj+C dans la disposition de JAWS et Window-Eyes) : Titre pour la piste
  en cours de lecture.
* C (disposition JAWS et Window-Eyes) : Bascule l'explorateur de chariot
  (visionneuse de playlist uniquement).
* D (R dans la disposition de JAWS) : Durée restante pour la playlist (si un
  message d’erreur est donné, se déplacer vers la visionneuse de playlist et
  puis tapez cette commande).
* E (G dans la disposition de Window-Eyes) : Statut de métadonnées en
  streaming.
* Maj+1 jusqu'à maj+4, maj+0 : Statut de Métadonnées individuelles en
  streaming URLs (0 est pour l'encodeur DSP).
* E (disposition de Window-Eyes) : Temps écoulé pour la piste en cours de
  lecture.
* F : Recherche de piste (visionneuse de playlist uniquement).
* H : Durée de la musique pour la tranche horaire en cours.
* Maj+H : Durée des pistes restantes pour la tranche horaire.
* I (L dans la disposition de JAWS ou Window-Eyes) : Nombre d'auditeurs.
* K : Se déplacer à la piste marquée (visionneuse de playlist uniquement).
* Contrôle+K : Définir la piste en cours comme le marqueur de position de
  piste (visionneuse de playlist uniquement).
* L (Maj+L dans la  disposition de JAWS et Window-Eyes) : Entrée ligne.
* M : Microphone.
* N : Titre pour la piste suivante planifié.
* P : Statut (en cours de lecture ou arrêté).
* Maj+P : Hauteur de la piste actuelle.
* R (Maj+E dans la disposition  de JAWS et Window-Eyes) : Enregistrer dans
  un fichier activé/désactivé.
* Maj+R : Contrôle du balayage de la bibliothèque en cours.
* S : Piste débute (planifié).
* Maj+S : Durée jusqu'à la piste sélectionnée qui va être jouer (piste
  débute dans).
* T : Mode édition/insertion chariot activé/désactivé.
* U: temps de fonctionnement Studio.
* W: Météo et température si configurée.
* Y: Statut de la modification de la playlist.
* 1 through 0: Announce column content for a specified column.
* F8 : Prendre des instantanés de playlist (nombre de pistes, piste la plus
  longue, etc.).
* Maj+F8 : Demander des transcriptions de playlist dans de nombreux formats.
* F9 : Marquer la piste en cours pour le début de l'analyse de playlist
  (visionneuse de playlist uniquement).
* F10 : Effectuer une analyse de durée de piste (visionneuse de playlist
  uniquement).
* F12 : basculer entre un profil en cours et un profil prédéfini.
* F1: Aide couche.
* Maj+F1 : Ouvre le guide de l'utilisateur en ligne.

## Contrôleur SPL

Le contrôleur SPL est un ensemble de commandes couches que vous pouvez
utiliser pour contrôler SPL Studio de n'importe où. Appuyez sur la commandes
couche Contrôleur SPL, et NVDA dira, "Contrôleur SPL." Appuyez sur une autre
commande pour contrôler divers paramètres Studio comme activer/désactiver un
microphone ou lire la piste suivante.

Les commandes disponibles pour le Contrôleur SPL sont:

* Appuyez sur P pour lire la suivante piste sélectionnée.
* Appuyez sur U pour mettre en pause ou pour reprendre la lecture.
* Appuyer sur S pour arrêter la piste avec fondu enchaîné, ou pour arrêter
  la piste instantanément, appuyez sur T.
* Appuyer sur M ou Maj+M pour activer ou désactiver le microphone,
  respectivement, ou appuyez sur N pour activer le microphone sans fondu.
* Appuyer sur A pour activer l'automatisation ou Maj+A pour désactiver
  celle-ci.
* Appuyer sur L pour activer l'entrée ligne ou Maj+L pour désactiver
  celle-ci.
* Appuyez sur R pour entendre le temps restant pour la piste en cours de
  lecture.
* Appuyez sur Maj+R pour obtenir un rapport sur  l'avancement du balayage de
  la bibliothèque.
* Appuyez sur C pour laisser NVDA annoncer le nom et la durée de la piste en
  cours de lecture.
* Appuyez sur Maj+C pour laisser NVDA annoncer le nom et la durée de la
  prochaine piste, le cas échéant.
* Press E to hear which encoders are connected.
* Appuyez sur I pour obtenir le nombre d'auditeurs.
* Appuyer sur Q pour obtenir diverses informations du statut de Studio, y
  compris si une piste est en cours de lecture, le microphone est activé et
  d'autres.
* Appuyez sur les touches de chariot (F1, Contrôle+1, par exemple) pour lire
  les chariots assignés à partir de n'importe où.
* Appuyez sur H pour afficher un dialogue d'aide répertoriant les commandes
  disponibles.

## Alarmes de la piste

By default, NVDA will play a beep if five seconds are left in the track
(outro) and/or intro. To configure this value as well as to enable or
disable them, press Alt+NVDA+1 or Alt+NVDA+2 to open end of track and song
ramp dialogs, respectively. In addition, use Studio add-on settings dialog
to configure if you'll hear a beep, a message or both when alarms are turned
on.

## Alarme microphone

Vous pouvez demander à NVDA de lire un son lorsque le microphone est actif
depuis un certain temps. Appuyez sur Alt+NVDA+4 pour configurer l'heure de
l'alarme en secondes (0 désactive celui-ci).

## Chercheur de piste

Si vous souhaitez trouver rapidement une chanson par artiste ou par nom de
chanson, depuis la liste de piste, appuyez sur Contrôle+NVDA+F. Tapez le nom
de l'artiste ou le nom de la chanson. NVDA va vous placer soit à la chanson
Si cell-ci est trouvé ou il affichera une erreur si elle ne trouve pas la
chanson que vous recherchez. Pour trouver une chanson ou un artiste
précédemment entrée, appuyez sur NVDA+F3 ou NVDA+Maj+F3 Pour trouver en
avant ou en arrière.

Remarque: le Chercheur de piste est sensible à la casse.

## Explorateur de Chariot

Selon l'édition, SPL Studio permet d'assigné jusq'à 96 chariots pendant la
lecture. NVDA vous permet d'entendre quel chariot ou jingle est assigné à
ces commandes.

To learn cart assignments, from SPL Studio, press Alt+NVDA+3. Pressing the
cart command once will tell you which jingle is assigned to the
command. Pressing the cart command twice will play the jingle. Press
Alt+NVDA+3 to exit cart explorer. See the add-on guide for more information
on cart explorer.

## Analyse de durée de piste

Pour obtenir la longueur pour jouer les pistes sélectionnés, marquer la
piste en cours pour le début de l'analyse de durée de piste (Assistant SPL,
F9), puis appuyer sur Assistant SPL, F10 lorsque vous atteignez la fin de la
sélection.

## Explorateur de Colonnes

En appuyant sur Contrôle+NVDA+1 jusqu'à 0 ou Assistant SPL, 1 jusqu'à 0,
vous pouvez obtenir le contenu des colonnes spécifiques. Par défaut ce sont
artiste, titre, durée, intro, catégorie nom de fichier, année, album, genre
et heure prévue. Vous pouvez configurer les colonnes qui seront explorées
via le dialogue Explorateur de Colonnes trouvé dans le dialogue Paramètres
de l'extension.

## Instantanés de playlist

Vous pouvez appuyer sur Assistant SPL , F8 étant focalisée sur une playlist
dans Studio pour obtenir diverses statistiques sur une playlist, y compris
le nombre de pistes dans la playlist, la piste la plus longue, les meilleurs
artistes et ainsi de suite.

## Transcriptions de Playlist

En appuyant sur Assistant SPL, Maj+F8 présentera une boîte de dialogue pour
vous permettre de demander des transcriptions de playlist dans de nombreux
formats, y compris dans un format de texte brut, un tableau HTML ou une
liste.

## Boîte de dialogue configuration

Depuis la fenêtre studio, vous pouvez appuyer sur Alt+NVDA+0 pour ouvrir la
boîte de dialogue configuration de l'extension. Sinon, allez dans le menu
préférences de NVDA et sélectionnez l'élément Paramètres SPL Studio. Cette
boîte de dialogue est également utilisé pour gérer les profils de diffusion.

## Mode tactile SPL

Si vous utilisez Studio sur un ordinateur possédant un écran tactile
fonctionnant sous Windows 8 ou version ultérieure et NVDA 2012.3 ou version
ultérieure installé, vous pouvez exécuter certaines commandes Studio depuis
un écran tactile. Tout d'abord utiliser une tape à trois doigts pour
basculer en mode SPL, puis utilisez les commandes tactile énumérées
ci-dessus pour exécuter des commandes.

## Version 20.01

* NVDA 2019.3 or later is required due to extensive use of Python 3.

## Version 19.11.1/18.09.13-LTS

* Initial support for StationPlaylist suite 5.40.
* In Studio, playlist snapshots (SPL Assistant, F8) and various time
  announcement commands such as remaining time (Control+Alt+T) will no
  longer cause NVDA to play error tones or do nothing if using NVDA 2019.3
  or later.
* In Creator's track list items, "Language" column added in Creator 5.31 and
  later is properly recognized.
* In various lists in Creator apart from track list, NVDA will no longer
  announce odd column information if Control+NVDA+number row command is
  pressed.

## Version 19.11

* Encoder status command from SPL Controller (E) will announce connection
  status for the active encoder set instead of encoders being monitored in
  the background.
* NVDA will no longer appear to do nothing or play error tones when it
  starts while an encoder window is focused.

## Version 19.10/18.09.12-LTS

* Shortened the version announcement message for Studio when it starts.
* Version information for Creator will be announced when it starts.
* 19.10: custom command can be assigned for encoder status command from SPL
  Controller (E) so it can be used from everywhere.
* Initial support for AltaCast encoder (Winamp plugin and must be recognized
  by Studio). Commands are same as SPL Encoder.

## Version 19.08.1

* In SAM encoders, NVDA will no longer appear to do nothing or play error
  tones if an encoder entry is deleted while being monitored in the
  background.

## Version 19.08/18.09.11-LTS

* 19.08: NVDA 2019.1 or later is required.
* 19.08: NVDA will no longer appear to do nothing or play error tones when
  restarting it while Studio add-on settings dialog is open.
* NVDA will remember profile-specific setttings when switching between
  settings panels even after renaming the currently selected broadcast
  profile from add-on settings.
* NVDA will no longer forget to honor changes to time-based profiles when OK
  button is pressed to close add-on settings. This bug has been present
  since migrating to multi-page settings in 2018.

## Version 19.07/18.09.10-LTS

* Renamed the add-on from "StationPlaylist Studio" to "StationPlaylist" to
  better describe apps and features supported by this add-on.
* Améliorations de la sécurité interne.
* If microphone alarm or metadata streaming settings are changed from add-on
  settings, NVDA will no longer fail to apply changed settings. This
  resolves an issue where microphone alarm did not start or stop properly
  after changing settings via add-on settings.

## Version 19.06/18.09.9-LTS

Version 19.06 supports SPL Studio 5.20 and later.

* Initial support for StationPlaylist Streamer.
* While running various Studio apps such as Track Tool and Studio, if a
  second instance of the app is started and then exits, NVDA will no longer
  cause Studio add-on configuration routines to produce errors and stop
  working correctly.
* Added labels for various options in SPL Encoder configuration dialog.

## Version 19.04.1

* Fixed several issues with redesigned column announcements and playlist
  transcripts panels in add-on settings, including changes to custom column
  order and inclusion not being reflected when saving and/or switching
  between panels.

## Version 19.04/18.09.8-LTS

* Various global commands such as entering SPL Controller and switching to
  Studio window will be turned off if NVDA is running in secure mode or as a
  Windows Store application.
* 19.04: in column announcements and playlist transcripts panels (add-on
  settings), custom column inclusion/order controls will be visible up front
  instead of having to select a button to open a dialog to configure these
  settings.
* In Creator, NVDA will no longer play error tones or appear to do nothing
  when focused on certain lists.

## Version 19.03/18.09.7-LTS

* L'appui sur Contrôle+NVDA+R pour recharger les paramètres sauvegardés
  rechargera maintenant aussi les paramètres de l'extension Studio, et un
  triple appui sur cette commande réinitialisera également les paramètres
  par défaut de l'extension Studio ainsi que les paramètres NVDA.
* Le dialogue de paramètres de l'extension Studio "Options avancées" a été
  renommé en "Avancé".
* 19.03 Expérimental : dans les panneaux d'annonces de colonnes
  transcription de playlists (paramètres de l'extension), les contrôles
  d'inclusion/ordre de personnalisation des colonnes seront visible au
  premier plan au lieu d'avoir à sélectionner un bouton pour ouvrir un
  dialogue pour configurer ces paramètres.

## Version 19.02

* Suppression de la fonctionnalité de vérification de mise à jour autonome
  de l'extension y compris la commande de vérification de mise à jour à
  partir de l'Assistant SPL (Contrôle+Maj+U) et les options de vérification
  de mise à jour à partir des paramètres de l'extension. La vérification de
  mise à jour de l'extension est maintenant effectuée par Add-on Updater.
* NVDA ne semble plus rien faire ou ne lit plus une tonalité d'erreur
  lorsque l'intervalle d'activation du microphone est défini, il est utilisé
  pour se souvenir lors de la diffusion que le microphone est actif avec des
  bips périodiques.
* Lors de la réinitialisation des paramètres de l'extension à partir du
  dialogue Paramètres extension / panneau réinitialisation, NVDA demandra à
  nouveau si un changement de profil immédiat ou un profil basé sur l'heure
  est actif.
* After resetting Studio add-on settings, NVDA will turn off microphone
  alarm timer and announce metadata streaming status, similar to after
  switching between broadcast profiles.

## Version 19.01.1

* NVDA n'annoncera plus "Contrôle du balayage de la bibliothèque en cours"
  après la fermeture de Studio dans certaines situations.

## Version 19.01/18.09.6-LTS

* NVDA 2018.4 ou ultérieur est requis.
* Davantage de changements de code pour rendre l'extension compatible avec
  Python 3.
* 19.01: certaines traductions de message de cette extension ressembleront à
  des messages NVDA.
* 19.01: la fonctionnalité Rechercher les mises à jour de l'extension n'est
  plus disponible. Un message d'erreur apparaît lorsque vous essayez
  d'utiliser l'Assistant SPL, Contrôle+Maj+U pour rechercher des mises à
  jour. Pour les futures mises à jour, veuillez utiliser l'extension Add-on
  Updater.
* Légères améliorations des performances lors de l'utilisation de NVDA avec
  des applications autres que Studio lorsque Voice Track Recorder est
  actif. NVDA continuera d'afficher des problèmes de performances lors de
  l'utilisation de Studio lui-même avec Voice Track Recorder actif.
* Dans les encodeurs, si un dialogue Paramètres de l'encodeur est ouvert
  (Alt+NVDA+0), NVDA affichera un message d'erreur si vous essayez d'ouvrir
  un eautre dialogue Paramètres de l'encodeur.

## Version 18.12

* Changements internes afin de rendre l'extension compatible avec les
  futures versions de NVDA.
* Correction de nombreuses occurrences de messages de l'extension annoncés
  en anglais malgré leur traduction dans d'autres langues.
* Si vous utilisez l'Assistant SPL pour rechercher des mises à jour de
  l'extension (Assistant SPL, Contrôle+Maj+U), NVDA n'installe pas de
  nouvelles versions de l'extension si elles nécessitent une version plus
  récente de NVDA.
* Certaines commandes de l'assistant SPL exigent désormais que la
  visionneuse de playlist soit visible et complété par une playlist. Dans
  certains cas, une piste est focalisée. Les commandes concernées incluent
  la durée restante (D), les instantanés de playlist (F8) et les
  transcriptions de Playlist (Maj + F8).
* La commande pour la durée restante de la playlist (Assistant SPL, D) exige
  désormais qu'une piste depuis la visionneuse de playlist soit focalisée.
* Dans les encodeurs de SAM, vous pouvez désormais utiliser les commandes de
  navigation dans les tableaux (Contrôle+Alt+touches fléchées) pour examiner
  diverses informations sur l'état de l'encodeur.

## Version 18.11/18.09.5-LTS

Note: 18.11.1 remplace 18.11 afin de mieux prendre en charge Studio 5.31.

* Premier support de StationPlaylist Studio 5.31.
* Vous pouvez maintenant obtenir des instantanés de playlist (Assistant SPL,
  F8) et des transcriptions (Assistant SPL, Maj+F8) alors qu'une playlist
  est chargée mais la première piste n'a pas le focus.
* NVDA ne semblera plus rien faire et ne jouera pas des tonalités d'erreur
  en essayant d'obtenir le statut de diffusion des métadonnées au démarrage
  de Studio s'il est configuré pour le faire.
* S'il est configuré pour annoncer l'état de la diffusion des métadonnées au
  démarrage , , l'annonce de l'état de diffusion des métadonnées et ne sera
  plus coupé les annonces relatives aux modifications de la barre d'état, et
  inversement.

## Version 18.10.2/18.09.4-LTS

* Correction de l'incapacité de fermer l'écran Paramètres de l'extension si
  le bouton Appliquer a été appuyé et que les boutons OK ou Annuler ont
  ensuite été pressés.

## Version 18.10.1/18.09.3-LTS

* Résolution de plusieurs problèmes liés à la fonction de l'annonce de
  connexion de l'encodeur, y compris le fait de ne pas annoncer les statut
  des messages, de ne pas lire la première piste sélectionnée ou de ne pas
  basculer à la fenêtre Studio lorsqu'il est connectée. Ces bugs sont causés
  par wxPython 4 (NVDA 2018.3 ou ultérieur).

## Version 18.10

* NVDA 2018.3 ou ultérieur est requis.
* Changements internes afin de rendre l'extension plus compatible avec
  Python 3.

## Version 18.09.1-LTS

* Lors de l'obtention de transcriptions de playlist au format de tableau
  HTML, les titres de colonnes ne sont plus affichés sous la forme d'une
  chaîne de liste Python.

## Version 18.09-LTS

La version 18.09.x est la dernière série à prendre en charge Studio 5.10 et
elle est basée sur les anciennes technologies, avec la 18.10 et versions
ultérieures prenant en charge Studio 5.11 / 5.20 et des nouvelles
fonctionnalités si nécessaire, certaines nouvelles fonctionnalités seront
redirigées vers la 18.09.x.

* NVDA 2018.3 ou une version ultérieure est recommandée en raison de
  l'introduction de wxPython 4.
* L'écran des paramètres des extensions est désormais entièrement basé sur
  une interface multi-pages dérivée de NVDA 2018.2 et versions ultérieures.
* Test Drive Fast et Slow ont combiné le canal "développement" avec une
  option permettant aux utilisateurs de snapshot  de développement de tester
  les fonctionnalités pilotes en cochant la nouvelle case à cocher
  "Fonctions pilotes" du panneau Paramètres avancés. Les utilisateurs
  d'abord sur Test Drive Fast Ring continuera à tester les fonctionnalités
  du pilote.
* La possibilité de sélectionner un canal différent pour la mise à jour de
  l'extension à partir des paramètres de l'extension a été supprimée. Les
  utilisateurs qui souhaitent basculer vers un canal de version différent
  devraient visiter le site comunautaire des extensions NVDA
  (addons.nvda-project.org), sélectionnez StationPlaylist Studio, puis
  téléchargez la version appropriée.
* Les cases à cocher d'inclusion de colonne pour l'annonce de colonne et les
  transcriptions de playlist, ainsi que les cases à cocher pour les flux de
  métadonnées ont été converties en contrôles de liste vérifiables.
* When switching between settings panels, NVDA will remember current
  settings for profile-specific settings (alarms, column announcements,
  metadata streaming settings).
* Ajout du format CSV (valeurs séparées par des virgules) en tant que format
  de transcriptions de playlist.
* En appuyant sur Ctrl+NVDA+C pour enregistrer les paramètres, vous
  sauvegarderez également les paramètres de l'extension Studio (nécessite
  NVDA 2018.3).

## Version 18.08.2

* NVDA ne vérifie plus les mises à jour de l'extension Studio si l'extension
  Add-on Updater (preuve de concept) est installée. Par conséquent, les
  paramètres de l'extension n'incluent plus les paramètres associés à la
  mise à jour de l'extension, si c'est le cas. Si vous utilisez Add-on
  Updater, vous devez utiliser les fonctionnalités fournies par cette
  extension pour vérifier les mises à jour de l'extension Studio.

## Version 18.08.1

* Correction d'un autre problème de compatibilité avec wxPython 4 constaté
  lors de la fermeture de Studio.
* NVDA annoncera un message approprié lorsque le texte de modification de la
  playlist n'est pas présent, généralement vu après le chargement d'une
  playlist non modifiée ou lorsque Studio démarre.
* NVDA ne semblera plus rien faire et ne jouera pas des tonalités d'erreur
  en essayant d'obtenir le statut de diffusion des métadonnées via
  l'Assistant SPL (E).

## Version 18.08

* Le dialogue des paramètres de l'extension est désormais basée sur
  l'interface des paramètres multi-catégories de NVDA 2018.2. Par
  conséquent, cette version nécessite NVDA 2018.2 ou une version
  ultérieure. L'ancienne interface de paramètres de l'extension est obsolète
  et sera supprimée plus tard en 2018.
* Ajout d'une nouvelle section (bouton / panneau) dans les Paramètres
  extension pour configurer les options de transcriptions de playlist, qui
  est utilisée pour configurer l'inclusion et l'organisation de colonne pour
  cette fonctionnalité et d'autres paramètres.
* Lors de la création de transcriptions de playlist basées sur des tableaux
  et si l'organisation de colonne personnalisée et / ou la suppression de
  colonne est activée, NVDA utilisera l'ordre de présentation des colonnes
  personnalisé spécifié dans les Paramètres  extension et / ou n'inclura pas
  les informations des colonnes supprimées.
* Lors de l'utilisation des commandes des éléments de piste de la colonne de
  navigation (Contrôle+Alt+début / fin / flèche gauche / flèche droite) dans
  Studio, Créateur et l'Outil de piste, NVDA ne va plus annoncer la colonne
  de données erronées après avoir changé la position de la colonne sur
  l'écran via la souris.
* Amélioration significative de la réactivité de NVDA lors de l'utilisation
  des commandes de navigation par colonnes dans Creator et l'Outil de
  piste. En particulier, lors de l'utilisation de Creator, NVDA répondra
  mieux en utilisant les commandes de navigation par colonne.
* NVDA ne lira plus les tonalités d'erreur ou ne semblera rien faire lorsque
  vous tentez d'ajouter des commentaires à des pistes dans Studio ou lorsque
  vous quittez NVDA en utilisant Studio, causé par le problème de
  compatibilité wxPython 4.

## Version 18.07

* Ajout d'un écran expérimental de Paramètres multi-catégories de
  l'extension, accessible en basculant sur Paramètre dans les Paramètres
  extension / dialogue Avancé (vous devez redémarrer NVDA après avoir
  configuré ce paramètre pour que la nouvelle boîte de dialogue
  apparaisse). Ceci est destiné aux utilisateurs de NVDA 2018.2 et tous les
  paramètres de l'extension ne peuvent pas être configurés à partir de ce
  nouvel écran.
* NVDA ne lira plus les tonalités d'erreur ou ne fera rien lorsque vous
  essayez de renommer un profil de diffusion à partir des paramètres
  extension, causés par le problème de compatibilité wxPython 4.
* When restarting NVDA and/or Studio after making changes to settings in a
  broadcast profile other than normal profile, NVDA will no longer revert to
  old settings.
* Il est maintenant possible d'obtenir des transcriptions de playlist pour
  l'heure actuelle. Sélectionnez "heure actuelle" dans la liste des options
  de l'intervalle de playlist dans la boîte de dialogue Transcriptions de
  Playlist (Assistant SPL, Maj+F8).
* Ajout d'une option dans le dialogue Transcriptions de Playlist pour que
  les transcriptions soient enregistrées dans un fichier (tous les formats)
  ou copiées dans le presse-papiers (formats de tableau texte et Markdown
  uniquement) en plus de visualiser les transcriptions à l'écran. Lorsque
  les transcriptions sont enregistrées, elles sont enregistrées dans le
  dossier Documents de l'utilisateur sous le sous-dossier
  "nvdasplPlaylistTranscripts".
* La colonne Statut n'est plus incluse lors de la création des
  transcriptions de playlist dans les formats de tableau HTML et Markdown.
* Quand a été mis en focus sur une piste dans Creator et l'Outil de piste,
  en appuyant sur Contrôle+NVDA+rangée numérique présente des informations
  de colonne sur une fenêtre en mode navigation.
* Dans Creator et l'Outil de piste, ajoutés les touches
  Contrôle+Alt+début/fin pour déplacer le Navigateur de Colonne à la
  première ou la dernière colonne pour la piste focalisée.

## Version 18.06.1

* Correction de plusieurs problèmes de compatibilité avec wxPython 4,
  notamment l'impossibilité d'ouvrir le Chercheur de piste
  (Contrôle+NVDA+F), les boîtes de dialogue Recherche de colonne et
  Recherche de l'intervalle de temps dans Studio et la boîte de dialogue
  d'étiquetage de flux (F12) à partir de la fenêtre des encodeurs.
* Lors de l'ouverture pour trouver une boîte de dialogue à partir de Studio
  et une erreur inattendue se produit, NVDA présentera des messages plus
  appropriés au lieu de dire qu'une autre boîte de dialogue de recherche est
  ouverte.
* Dans la fenêtre des encodeurs, NVDA ne lira plus de tonalités td'erreur ou
  semblera ne rien faire en tentant d'ouvrir la boîte de dialogue des
  paramètres de l'encodeur (Alt+NVDA+0).

## Version 18.06

* Dans les paramètres de l'extension, ajout du bouton "Appliquer" afin que
  les modifications apportées aux paramètres puissent être appliquées au
  profil actuellement sélectionné et / ou actif sans fermer le dialogue en
  premier. Cette fonctionnalité est disponible pour les utilisateurs de NVDA
  2018.2.
* Résolution d'un problème où NVDA appliquerait des modifications aux
  paramètres de l'Explorateur de colonnes malgré l'activation du bouton
  Annuler dans le dialogue Paramètres de l'extension.
* Dans Studio, lorsque vous appuyez deux fois sur Contrôle+NVDA+rangée
  numérique alors que a été mis en focus sur une piste, NVDA affiche des
  informations de colonne pour une colonne spécifique dans une fenêtre en
  mode navigation.
* Alors que a été mis en focus sur une piste dans Studio, appuyez sur
  Contrôle+NVDA+Tiret pour afficher les données de toutes les colonnes d'une
  fenêtre en mode navigation.
* Dans StationPlaylist Creator, lorsque a été mis en focus sur une piste en
  appuyant sur Contrôle+NVDA+rangée numérique annoncera les données dans une
  colonne spécifique.
* Ajout d'un bouton dans les paramètres de l'extension pour configurer
  l'explorateur de colonnes pour SPL Creator.
* Ajout du format de tableau Markdown en tant que format de transcriptions
  de playlist.
* La commande pour le retour de commentaires au développeur a changé de
  Contrôle+NVDA+tiret à Alt+NVDA+tiret.

## Version 18.05

* Ajout de la possibilité de prendre des instantanés partiels de
  playlist. Cela peut être fait en définissant la plage d'analyse (Assistant
  SPL, F9 au début de la plage d'analyse) et en déplaçant vers un autre
  élément et en exécutant la commande instantanés de playlist.
* Ajout d'une nouvelle commande dans l'Assistant SPL pour demander des
  transcriptions de playlist dans un certain nombre de formats
  (Maj+F8). Ceux-ci incluent du texte brut, un tableau HTML ou une liste
  HTML.
* Diverses fonctions d'analyse des playlist, telles que l'analyse de durée
  de piste et les instantanés de playlist, sont désormais regroupées sous le
  thème "Analyseur de Playlist".

## Version 18.04.1

* NVDA ne cessera plus de démarrer le compte à rebours pour les profils de
  diffusion basés sur l'heure si NVDA avec wxPython 4 toolkit installé est
  en cours d'utilisation.

## Version 18.04

* Des modifications ont été apportées pour rendre la fonction de
  vérification des mises à jour de l'extension plus fiable, en particulier
  si la vérification automatique des mises à jour de l'extension est
  activée.
* NVDA émet une tonalité pour indiquer le début du balayage de la
  bibliothèque lorsqu'il est configuré pour lire des bips pour diverses
  annonces.
* NVDA démarre l'analyse de la bibliothèque en arrière-plan si l'analyse de
  la bibliothèque est démarrée à partir du dialogue Options de Studio ou au
  démarrage.
* Tapoter deux fois sur une piste sur un ordinateur à écran tactile ou si
  vous exécutez une commande d'action par défaut, la piste sera sélectionnée
  et va déplacer le focus système sur celle-ci.
* Lorsque vous prenez des instantanés de playlist (Assistant SPL, F8), si
  une playlist contient uniquement des marqueurs d'heure, elle résout
  plusieurs problèmes pour lesquels NVDA ne semblait pas prendre
  d'instantanés.

## Version 18.03/15.14-LTS

* Si NVDA est configuré pour annoncer l'état de la diffusion des métadonnées
  au démarrage de Studio, NVDA respectera ce paramètre et n'annoncera plus
  l'état de diffusion lors du basculement vers et à partir du changement de
  profil immédiat.
* Si le basculement vers et à partir d'un changement de profil immédiat et
  NVDA est configuré pour annoncer l'état de la diffusion des métadonnées à
  chaque fois que cela se produit, NVDA n'annoncera plus ces informations
  plusieurs fois lors du basculement rapide des profils.
* NVDA se rappellera de basculer au profil basé sur l'heure approprié (si
  défini pour un affichage) après que NVDA redémarre plusieurs fois pendant
  les diffusions.
* Si un profil basé sur l'heure avec la durée du profil est activé et que le
  dialogue paramètres de l'extension est ouvert et fermé, NVDA retournera au
  profil d'origine une fois le profil basé sur l'heure terminée.
* Si un profil basé sur l'heure est actif (en particulier pendant les
  diffusions), il ne sera pas possible de modifier les déclencheurs de
  profil de diffusion via le dialogue Paramètres de l'extension.

## Version 18.02/15.13-LTS

* 18.02 : En raison de modifications internes apportées pour prendre en
  charge les points d'extension et d'autres fonctionnalités, NVDA 2017.4 est
  requis.
* La mise à jour de l'extension ne sera pas possible dans certains cas. Cela
  inclut l'exécution de NVDA à partir du code source ou avec le mode
  sécurisé activé. La vérification du mode sécurisé s'applique également à
  la 15.13-LTS.
* Si des erreurs se produisent lors de la vérification des mises à jour,
  celles-ci seront sauvegardées et NVDA vous conseillera de lire le journal
  (log) de NVDA pour plus de détails.
* Dans les paramètres de l'extension, divers paramètres de mise à jour dans
  la section des paramètres avancés, tels que l'intervalle de mise à jour,
  ne seront pas affichés si la mise à jour des extensions n'est pas prise en
  charge.
* NVDA ne semblera plus se bloquer ou ne fera plus rien lors du basculement
  à un changement de profil immédiat ou à un profil basé sur l'heure et NVDA
  est configuré pour annoncer l'état de diffusion des métadonnées.

## Version 18.01/15.12-LTS

* Lors de l'utilisation de la disposition de JAWS pour l'Assistant SPL, la
  commande pour rechercher les mises à jour (Contrôle+Maj+U) fonctionne
  désormais correctement.
* Lorsque vous modifiez les paramètres alarme microphone via le dialogue
  alarme (Alt+NVDA+4), des modifications telles que l'activation de l'alarme
  et la modification de l'intervalle d'alarme sont appliquées à la fermeture
  du dialogue.

## Version 17.12

* Windows 7 Service Pack 1 ou ultérieur est requis.
* Several add-on features were enhanced with extension points. This allows
  microphone alarm and metadata streaming feature to respond to changes in
  broadcast profiles. This requires NVDA 2017.4.
* Lorsque Studio se ferme, divers dialogues de l'extension tels que les
  paramètres de l'extension, les dialogues d'alarme et autres se ferment
  automatiquement. Cela nécessite NVDA 2017.4.
* Ajout d'une nouvelle commande dans la Couche Contrôleur SPL pour annoncer
  le nom de la prochaine piste, le cas échéant (Maj+C).
* Vous pouvez maintenant appuyer sur les touches du chariot (F1, par
  exemple) après avoir entrée la Couche Contrôleur SPL pour lire les
  chariots assignés de n'importe où.
* En raison des changements introduits dans la boîte à outils GUI de
  wxPython 4, le dialogue pour effacer les étiquettes de flux est maintenant
  une zone de liste déroulante au lieu d'un champ d'entrée de nombre.

## Version 17.11.2

Ceci est la dernière version stable à prendre en charge Windows XP, Vista et
7 sans Service Pack 1. La prochaine version stable pour ces versions de
Windows sera une version 15.x LTS.

* Si vous utiliser les versions de Windows antérieures à Windows 7 Service
  Pack 1, vous ne pouvez pas basculer vers les canaux de développement.

## Version 17.11.1/15.11-LTS

* NVDA ne lira plus les tonalités d'erreur ou ne semblera rien faire lors de
  l'utilisation des touches  Contrôle+Alt+flèches gauche ou droite pour
  naviguer dans les colonnes de l'Outil de Piste 5.20 avec une piste
  chargée. En raison de cette modification, lorsque vous utilisez Studio
  5.20, la version 48 ou ultérieure est requise.

## Version 17.11/15.10-LTS

* Premier support de StationPlaylist Studio 5.30.
* Si l'alarme microphone et/ou la minuterie d'intervalle est activée et si
  Studio quitte pendant que le microphone est activé, NVDA ne jouera plus de
  tonalité d'alarme microphone de partout.
* Lors de la suppression de profils de diffusion et si un autre profil se
  trouve être un changement de profil immédiat, l'indicateur de changement
  immédiat ne sera pas supprimé du changement de profil.
* Si vous supprimez un profil actif qui n'est pas un changement immédiat ou
  un profil basé sur l'heure, NVDA demandera une fois de plus une
  confirmation avant de continuer.
* NVDA appliquera les paramètres corrects pour les paramètres alarme
  microphone lors des changements de profils via le dialogue de Paramètres
  de l'extension.
* Vous pouvez maintenant appuyer sur Contrôleur SPL, H pour obtenir de
  l'aide sur la couche Contrôleur SPl.

## Version 17.10

* Si vous utiliser les versions de Windows antérieures à Windows 7 Service
  Pack 1, vous ne pouvez pas basculer au canal de mise à jour de Test Drive
  Fast. Une version future de cette extension déplacera les utilisateurs des
  anciennes versions de Windows vers un canal de prise en charge dédié.
* Plusieurs paramètres généraux tels que le statut de l'annonce en bips, en
  haut et en bas de la notification de playlist et d'autres se trouvent
  maintenant situés dans le nouveau dialogue Paramètres généraux de
  l'extension (accessible à partir d'un nouveau bouton dans les paramètres
  de l'extension).
* Il est maintenant possible de mettre les options de l'extension en lecture
  seule, utilisez uniquement le profil normal, ou de ne pas charger les
  paramètres à partir du disque lorsque Studio démarre. Ceux-ci sont
  contrôlés par de nouveaux commutateurs en ligne de commande spécifiques à
  cette extension.
* Lors de l'exécution de NVDA depuis le dialogue Exécuter (Windows+R), vous
  pouvez maintenant passer en ligne de commande supplémentaires les
  commutateurs pour modifier la façon dont l'extension fonctionne. Ces
  derniers comprennent "--spl-configvolatile" (paramètres en lecture seule),
  "--spl-configinmemory" (ne pas charger les paramètres du disque), et
  "--spl-normalprofileonly" (utiliser uniquement le profil normal).
* Si en sortant de Studio (pas de NVDA) pendant que le changement de profil
  immédiat est actif, NVDA ne donne plus d'annonces trompeurs lors du
  basculement à un changement de profil immédiat lors de l'utilisation de
  Studio à nouveau.

## Version 17.09.1

* À la suite de l'annonce de NV Access que NVDA 2017.3 sera la dernière
  version prise en charge avec les versions de Windows antérieures à
  Windows 7 Service Pack 1, l'extension Studio présentera un message de
  rappel à ce propos si vous exécuter sur d'anciennes versions de
  Windows. La fin de la prise en charge des anciennes versions de Windows
  pour cette extension (via une prise en charge de la version long-term) est
  prévue pour Avril 2018.
* NVDA n'affichera plus de dialogue de démarrage et/ou n'annoncera plus la
  version de Studio si elle a débuté avec un ensemble d'indicateurs minimal
  (nvda -rm). La seule exception est l'ancien dialogue de rappel de version
  de Windows.

## Version 17.09

* Si un utilisateur entre dans le dialogue des options avancées dans les
  paramètres de l'extenson, le canal et l'intervalle de mise à jour ont été
  définis sur Test Drive Fast et/ou zéro jours, NVDA ne présentera plus le
  message d'avertissement de canal et/ou d'intervalle en sortant de ce
  dialogue.
* Les commandes playlist restante et l'analyse de la durée de piste
  exigeront maintenant le chargement d'une playlist et un message d'erreur
  plus précis sera présenté autrement.

## Version 17.08.1

* NVDA ne sera plus en mesure de laisser Studio jouer la première piste
  lorsqu'un encodeur est connecté.

## Version 17.08

* Changements apportées à la mise à jour des étiquettes du canal : une build
  d'essai est maintenant Test Drive Fast, le canal de développement est Test
  Drive Slow. Les vraies builds "essai" seront réservées aux builds d'essai
  réelles qui nécessitent que les utilisateurs installent manuellement une
  version de test.
* L'intervalle de mise à jour peut maintenant être réglé sur 0 (zéro)
  jours. Cela permet à l'extension de vérifier les mises à jour lorsque NVDA
  et/ou SPL Studio démarrent. Une confirmation sera nécessaire pour modifier
  l'intervalle de mise à jour à zéro jours.
* NVDA ne parviendra plus à vérifier les mises à jour de l'extension si
  l'intervalle de mise à jour est réglé sur 25 jours ou plus.
* In add-on settings, added a checkbox to let NVDA play a sound when
  listener requests arrive. To use this fully, requests window must pop up
  when requests arrive.
* En appuyant sur la commande de temps de diffusion (NVDA+Maj+F12) deux
  fois, NVDA annoncera les minutes et les secondes restant dans l'heure
  actuelle.
* Il est maintenant possible d'utiliser Chercheur de piste (Control + NVDA +
  F) pour rechercher les noms des pistes que vous avez recherchées avant en
  sélectionnant un terme de recherche à partir d'un historique de termes.
* Lors de l'annonce du titre de la piste actuelle et suivante via
  l'Assistant SPL, il est maintenant possible d'inclure des informations sur
  le lecteur interne de Studio qui jouera la piste (par exemple, le lecteur
  1).
* Ajout d'un paramètre dans les paramètres de l'extension sous le statut des
  annonces pour inclure l'information du lecteur lors de l'annonce du titre
  de la piste actuelle et suivante.
* Correction d'un problème dans le caractère indicateur temporaire et
  d'autres dialogues où NVDA n'indiquerait pas de nouvelles valeurs lors de
  la manipulation des horodateurs.
* NVDA peut supprimer l'annonce des titres de colonne tels que l'artiste et
  la catégorie lors de la révision des pistes dans la visionneuse de
  playlist. Il s'agit d'un paramètre spécifique au profil de diffusion.
* Ajouté une case à cocher   dans la boîte de dialogue paramètres de
  l'extension pour supprimer l'annonce des titres de colonnes lors de la
  révision des pistes dans la visionneuse de playlist.
* Ajout d'une commande dans la Couche Contrôleur SPL pour annoncer le nom et
  la durée de la piste en cours de lecture de n'importe où (C).
* Lorsque vous obtenez des informations du statut via le Contrôleur SPL (Q)
  pendant l'utilisation de Studio 5.1x, des informations telles que le
  statut du microphone, mode édition chariot et d'autres seront également
  annoncées en plus de la lecture et de l'automatisation.

## Anciennes versions

S'il vous plaît voir le lien changelog pour les notes de version  pour les
anciennes versions de l'extension.

[[!tag dev stable]]

[1]: https://addons.nvda-project.org/files/get.php?file=spl

[2]: https://addons.nvda-project.org/files/get.php?file=spl-dev

[3]: https://addons.nvda-project.org/files/get.php?file=spl-lts18

[4]: https://github.com/josephsl/stationplaylist/wiki/SPLAddonGuide

[5]: https://github.com/josephsl/stationplaylist/wiki/splchangelog

[6]: https://addons.nvda-project.org/files/get.php?file=spl-2019
