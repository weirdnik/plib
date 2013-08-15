#!/bin/bash

MEVER="3.0.20130805001"

# prosty skrypcik, z gory przepraszam
# uwaga - skrypt sie automatycznie aktualizuje, mozna to ponizej gdzies wylaczyc
# Autor Robert Maron <robmar@robmar.net>
# Licencja Creative Commons (CC0) http://creativecommons.org/publicdomain/zero/1.0/

# do kompletu warto pobrac tez drugi skrypcik, tworzacy prostego HTMLa:
# http://robmar.net/process-blip-archive.sh

# wymagania: srodowisko GNU *nix, narzedzia grep, seq, wget, diff, itp. wersje GNU
# testowalem pod Linuksem, Mac Os X (+Fink/MacPorts), Windows (cygwin/MinGW)
# z jakiegos powodu pod Windows jest baaaaardzo wolne
# uwagi: w zasadzie nie ma obslugi bledow, pszpszm
# uwaga: jesli w jednym repo DATA/ trzymasz blipniecia kilku osob, to po 
#        aktualizacji do wersji 2.6 wykasuj caly folder i pobierz go ponownie

# Historia zmian:
# 3.0:
#   * korzystanie z dowolnego podanego hasla w command line do pobrania z wszystkich kont
#     rzeczy wymagajacych zalogowania (wiele rzeczy wymaga hasla, ale tylko tagi 
#     i wiadomosci prywatne wymagaja hasla tego uzytkownika, do reszty moze byc 
#     dowolne inne konto z haslem)
#   * pobieranie pelnej informacji o blipnieciach (url /s/) z lajkami, itp. 
#     - wymaga hasla, niestety dosc wolne
#   * przy pobieraniu calego blipniecia blipapi sie wywala, jesli choc jeden z 
#     lajkujacych skasowal konto; wiec wtedy probujemy pobrac bez lajkujacych
#     (uwaga: nie odtwarzam wstecz, skasuj plik DATA.full.<username> zeby ponowic
# 2.9:
#   * pobieranie list obserwowanych i obserwujacych, oraz tagow - jesli podane 
#     jest haslo
# 2.8:
#   * wczytywanie wiadomosci (prywatnych i publicznych) jesli poda sie haslo
#   * zawsze pobiera avatar, bo moze sie zmieniac
#   * drobne porzadki
# 2.7:
#   * zmiana liczby pobieranych wiadomosci w paczce (z 50 na 20) z powodu zmiany 
#     w api
#   * zmiana formatu przechowywanych rekordow (zachowane {})
#     uwaga: wymaga wykasowania folderu DATA, zeby weszla w zycie
#   * komentarz o process-blip-archive.sh
# 2.6:
#   * przyspieszenie pobierania
#   * obsluga linkow rdir (zachowanie zawartosci linkow)
#   * poprawka bledu w paternie seda (dzieki ^eliwurman!)
#   * komentarze i uwagi
#   * pobieranie avatara
# 2.5:
#   * jesli wystapi blad przy pobieraniu powinien zaczac ponownie od miesiaca
#     z bledem, a nie od nastepnego, jak poprzednie wersje
#   * pobranego pustego obrazka nie uwazamy za pobrany, jesli mamy druga szanse
#   * blad przy pobieraniu obrazka nie jest traktowany jako fatalny
#   * drobne poprawki w kodzie do debugowania
#   * timeout na wgeta
#   * poprawka bledu z usuwaniem plikow .ostatni
# 2.4:
#   * poprawka bledu z ' zamiast "
#   * zmiana User-Agent i X-Blip-Application [20121120012]
# 2.3:
#   * mozliwosc wolania z kilkoma usernejmami na raz
# 2.2:
#   * komentarz
#   * auto-update :)
# 2.1:
#   * poniewaz teraz archives zwraca mi wpisy chronologicznie, to zmienilem 
#     kod obslugujacy inkrementalne pobieranie; nie ogarniam...
#   * drobne retusze
# 2.0:
#   * tworzy drzewo folderow w DATA, poprzednie (z wersji 1.0)  trzeba usunac
#   * mozna uruchamiac inkrementalnie, doczyta co nowe
#   * nie uzywa juz folderu CACHE
# 1.0:
#   * pierwsza wersja, 
#   * pobieranie archiwum do folderu DATA, 
#   * tworzy pomocniczy folder CACHE

# od kiedy pobierac
YSTART=2007

# ile max cyfr ma liczba blipniec na miesiac
CNT=4

# ile sekund czekac pomiedzy pobraniami; musi byc przynajmniej 1
SLEEP=2

# czy szukamy bledow w kodzie? (T/N)
DEBUG=N

# czy byc cicho? (T/N)
QUIET=N

# juz nie uzywamy tego katalogu ;)
CACHE=CACHE ; #if [ -d "$CACHE" ] ; then rm -rf "$CACHE" ; fi

# rekordy z wpisami
DATA=DATA ; mkdir -p "$DATA"

# folder na notatki (np. co juz pobrane)
NOTES="$DATA"/NOTES ; mkdir -p "$NOTES"

# folder na linki rdir i wartosci przekierowan
RDIR="$DATA"/RDIR
if [ ! -d "$RDIR" ] ; then
  NOWYRDIR="T"
  mkdir -p "$RDIR"
else
  NOWYRDIR="N"
fi

# czy ponownie przeleciec wszystkie katalogi
FORCEFULL=N

# foldery wiadomosci PRIV i PUBL maja nazwy zalezace od username, zdefiniowane sa dalej

# plik README
README=README

# znacznik na ostatni, niezamkniety (ale lepiej myslec "brudny") miesiac
OSTATNI="ostatni"

# log wgeta i ogolnie tego skryptu
LOG="$(basename $0)".log ; cp /dev/null "$LOG"

# plik z ciasteczkami (potrzebne przy pobieraniu obrazkow z prywatnych wiadomosci)
COOKIES=cookies-$$-$RANDOM.txt

# naglowki wymagane przez Blip API
H1='X-Blip-API: 0.02'
H2='Accept: application/json'
H3="X-Blip-Application: $(basename $0)"

# opcje do wgeta
WGETOPT="--timeout=5"

# URL do API
URLAPI='http://api.blip.pl'

# kontekst dla blipniec
URLS="s"

# opcje do pobrania blipniecia z lajkujacymi
WGETOPTSLIKES="include=likes_user"

# kontekst dla archiwum zdefiniowano dalej, bo zalezy od nazwy uzytkownika
#URLARCH="users/$U/archives"

# kontekst dla obserwowanych, dalej
#URLFROM="users/$U/subscriptions/from"

# kontekst dla obserwowanych, dalej
#URLTO="users/$U/subscriptions/to"

# kontekst dla tagow
URLTAGS="tag_subscriptions/subscribed"

# kontekst dla tagow ignorowanych
URLTAGSI="tag_subscriptions/ignored"

# kontekst dla wiadomosci prywatnych
URLPRIV="private_messages/since"

# kontekst dla wiadomosci publicznych, dalej
#URLPUBL="users/$U/directed_messages"

# limit jednoczesnie pobieranych wpisow z archiwum; max bylo 50, ostatnio zmieniali...
LIMIT=20

# User-Agent przy wolaniach API
UAGENT="$(basename $0)/$MEVER"

# obecny rok
YNOW="$(date +'%Y')"

# obecny miesiac
MNOW="$(date +'%m')"

# czy probowac aktualizacji?
AUTOUPDATE=T

# gdzie lezy najnowsza wersja tego skryptu?
MEMEME="http://robmar.net/get-blip-archive.sh"


##################################################################

# funkcje ogolne

# blip_echo ....
# wykonuje echo .... jesli nie jest w trybie QUIET
function blip_echo {
  if [ "$QUIET" != "T" ] ; then echo "$*" ; fi
}

# blip_echo_n ....
# wykonuje echo -n .... jesli nie jest w trybie QUIET
function blip_echo_n {
  if [ "$QUIET" != "T" ] ; then echo -n "$*" ; fi
}

# blip_sleep n
# czeka n sekund (n>0 koniecznie) wypisuje kropki...
function blip_sleep {
  if [ "$DEBUG" != "T" ] ; then
    for i in $(seq 1 $1) ; do
      blip_echo_n '.'
      sleep 1
    done
  fi
}

# blip_error desc
# zglasza na stderr blad z opisem desc
function blip_error {
  echo '' 1>&2
  echo '' 1>&2
  echo "$1" 1>&2
  echo '' 1>&2
}

# blip_fatal desc [kod]
# zglasza na stderr blad z opisem desc i przerywa prace z kodem kod lub 2
function blip_fatal {
  echo '' 1>&2
  echo '' 1>&2
  echo "$1" 1>&2
  echo '' 1>&2
  if [ $# -eq 2 ] ; then
    exit $2 # jesli podano drugi parametr to przerywam
  elif [ "$DEBUG" != "T" ] ; then
    exit 2 # jesli nie DEBUG
  else
    echo -n "Nacisnij ENTER " ; read # jesli DEBUG
  fi
  
}

# blip_debug desc
# wypisuje na stderr napis DEBUG: desc
function blip_debug {
  if [ "$DEBUG" = "T" ] ; then  
    echo "DEBUG: $1" 1>&2
  fi
}

##################################################################

# aktualizacja :)

# moja wersja
echo ""
echo "$(basename $0) wersja: $MEVER"
echo ""

if [ "$AUTOUPDATE" = "T" ] ; then

 # czy jest nowsza wersja?
 TMPME="get-blip-archive-new.sh"
 if ! wget $WGETOPT -U "$UAGENT" "$MEMEME" -o "$LOG" -O "$TMPME" ; then
  blip_error "nie moge sprawdzic nowszej wersji skryptu na $MEMEME"
 elif diff -q "$0" "$TMPME" > /dev/null ; then
  rm -f "$TMPME" # mamy najnowsza
 else
  if ! grep '^MEVER=' "$TMPME" ; then
    blip_error "Cos niepoprawnego sie pobralo, przerywam aktualizacje"
    rm -f "$TMPME"
  else
   TMPMEVER=$(grep '^MEVER=' "$TMPME" | cut -d "=" -f 2)
   echo ''
   echo "Jest dostepna inna wersja skryptu."
   echo "(masz $MEVER, jest dostepna $TMPMEVER)"
   echo -n "Czy uaktualnic skrypt (jesli mam uprawnienia?) T/N:"
   read A
   if [ "$A" = "t" ] || [ "$A" = "T" ] ; then
    if [ -w "$0" ] ; then # mozemy nadpisac
      echo -n "Skopiuje nowa wersje na $0, ok? T/N:"
      read A
      if [ "$A" = "t" ] || [ "$A" = "T" ] ; then
        if cp -f "$TMPME" "$0" ; then
          rm -f "$TMPME"
          echo "Ok, chyba sie udalo."
          echo -n "Nacisnij Enter, uruchomie nowa wersje "
          read
          echo ""
          exec "$0" "$@" # uruchamiam ponownie
        else
          blip_error "Nie udalo sie nadpisac $0"
          echo "Nowa wersja zostaje w pliku $TMPME"
        fi
      else # NIE 
        echo "Przerywam aktualizacje. Nowa wersja zostaje w pliku $TMPME"
      fi
    else # nie mamy uprawnien zapisu
      blip_error "Nie umiem nadpisac pliku $0; zachowuje nowa wersje w pliku $TMPME"
    fi
   else # NIE
     echo "Przerywam aktualizacje. Nowa wersja zostaje w pliku $TMPME"
   fi
  fi # niepoprawna nowa wersja
 fi # jest aktualizacja
fi # czy robic aktualizacje

##################################################################

# funkcje parsowania

# blip_extract_list
# usuwa ze stringu S nawiasy kwadratowe z pierwszego i ostaniego miejsca
# usuwa tez znaki nowego wiersza (i cr i lf) - bazujemy potem na tym
function blip_extract_list {
  S=$(echo "$S" | sed 's/^\[\(.*\)\]$/\1/g' | tr -d '\n\r')
}

# blip_get_one 
# pobiera ze stringu S jeden rekord i zapisuje go w S1
# uwaga: pobiera ostatni, bo tak mi latwiej
# uwaga: to ziterowane jest kwadratowe, ale na raz pobieramy tylko do 50 rekordow
# uwaga: wiec jakos to moze zadziala ;)
function blip_get_one {
  S1=$(echo "$S" | sed 's/^{.*},\({".*}\)$/\1/g')
  # ucinam S1 z konca
  S="${S:0:${#S}-${#S1}}"
  # zostalo cos? jesli tak, ucinamy przecinek z konca
  if [ -n "$S" ] ; then
    if [ ${S: -1} = ',' ] ; then
      S="${S:0:${#S} - 1}"
    else
      blip_debug ">${S:0:1}<"
      blip_fatal "nie wiem jak to sie stalo, ale nie znalazlem tu przecinka"
    fi
  fi
}

# blip_extract_record
# usuwa ze stringu S1 nawiasy klamrowe z pierwszego i ostaniego miejsca
function blip_extract_record {
  S1=$(echo "$S1" | sed 's/^{\(.*\)}$/\1/g')
}


##################################################################

# inne

# blip_cookie
# jesli trzeba, tworzy plik $COOKIES z sesja blipa, 
# potrzebne do obrazkow z prywatnych wiadomosci
function blip_cookie {
  if ! [ -f "$COOKIES" ] ; then
    TMPRES=logowanie-$$-$RANDOM.txt
    if ! wget --keep-session-cookies --save-cookies "$COOKIES" $WGETOPT -U "$UAGENT" -a "$LOG" -O "$TMPRES" http://blip.pl/signin ; then
      blip_error "Nie umiem pobrac strony logowania do blipa. Nie bedzie ciasteczka."
    else
      TOKEN=$(fgrep 'name="authenticity_token"' "$TMPRES" | sed 's/^.*input name="authenticity_token" type="hidden" value="\([^"]*\)".*$/\1/g')
      if ! wget --keep-session-cookies --load-cookies "$COOKIES" --save-cookies "$COOKIES" \
           $WGETOPT -U "$UAGENT" -a "$LOG" -O "$TMPRES" \
           --post-data "authenticity_token=$TOKEN&logging_in_user%5Blogin%5D=$U&logging_in_user%5Bpassword%5D=$P&logging_in_user%5Bremember%5D=1&x=45&y=18" \
           http://blip.pl/sessions ;
      then
        blip_error "Nie umiem zalogowac nas do blipa. Nie bedzie ciasteczka."
      else
        blip_debug "Ciasteczko utworzone"
      fi
    fi
    if [ -f "$TMPRES" ] ; then rm -f "$TMPRES" ; fi
  fi
}


##################################################################

# main :)

# jesli wywolano nas z kilkoma parametrami, to zalatwiamy je kolejno i NIE przechodzimy dalej
if [ $# -gt 1 ] ; then
  for i in "$@" ; do

    # uwaga: jesli parametr ma haslo, to przekazemy je do wszystkich wywolan po nim
    if [ "$ANYU" = "" ] && [[ "$i" == *:* ]] ; then
      export ANYU="${i%%:*}"
      export ANYP="${i#*:}"
    fi

    "$0" "$i"
  done
  exit # i koniec
fi

# tu jesli wywolano nas z co najwyzej jednym parametrem

# uzytkownik (haslo potrzebne tylko do wiadomosci - prywatnych i publicznych)
# sprawdzam, czy jest podane haslo (format: uzytkownik:haslo)
if [[ "$1" == *:* ]] ; then
  U="${1%%:*}"
  P="${1#*:}"
else
  U="$1"
  P=""
fi

# jesli mamy wlasne haslo, to nie uzywamy cudzego
if ! [ -z "$P" ] ; then
  ANYU="$U"; ANYP="$P"
fi

blip_debug "ANYU='$ANYU' ANYP='$ANYP'"
blip_debug "U='$U' P='$P'"

# weryfikacja danych

if [ -z "$U" ] ; then
  blip_echo  "Uzywaj tak: $(basename $0) nazwa_uzytkownika[:haslo] {nazwa_uzytkownika[:haslo]} ..."
  blip_echo  "Mozna wczesniej ustawic export ANYU=nazwa_uzytkownika ; export ANYP=haslo;"
  blip_echo  "ustawione w ANYU i ANYP, albo po prostu pierwsze uzyte w linii polecen"
  blip_echo  "haslo zostanie uzyte do pobrania danych wszystkich nastepnych uzytkownikow"
  blip_fatal "np.: $(basename $0) ala:ul ola jola:jurek" 5
fi

# kontekst dla archiwum (definiuje tu, bo zalezy od $U)
URLARCH="users/$U/archives"

# kontekst dla obserwowanych
URLFROM="users/$U/subscriptions/from"

# kontekst dla obserwowanych
URLTO="users/$U/subscriptions/to"

# kontekst dla wiadomosci publicznych
URLPUBL="users/$U/directed_messages"

# foldery na wiadomosci PRIV i PUBL (stworzymy je tylko, jesli jest haslo)
PRIV="$DATA"/"PRIV-$U"
PUBL="$DATA"/"PUBL-$U"

# sprawdzenie, czy nie trzeba czegos stworzyc

if [ ! -f "$DATA"/"$README" ] ; then
  echo "Foldery na lata, w nich na miesiace, tam pliki z blipnieciami i obrazkami." > "$DATA"/"$README"
  echo "Katalog NOTES to moje notatki, potrzebne przy ponownym przegladzie bliploga." >> "$DATA"/"$README"
fi

if ! [ -z "$ANYP" ] ; then
# czy byly juz pobierane pelne blipniecia?
if [ ! -f "$DATA"/"$README.full.$U" ] ; then
  FORCEFULL=T
  echo "Uwaga: pliki blip-$U-<id>-full.txt moga sie przydac do importu do #nowylepszyblip." > "$DATA"/"$README.full.$U"
fi
fi

if [ ! -f "$NOTES"/"$README" ] ; then
  echo "Ktore miesiace juz pobieralem i ktory jest ostatni (=niepelny)." > "$NOTES"/"$README"
  echo "Usun zawartosc, zeby ponownie przeskanowac bliplog." >> "$NOTES"/"$README"
fi

if [ ! -f "$RDIR"/"$README" ] ; then
  echo "Pobrane linki z http://rdir.pl/link" > "$RDIR"/"$README"
  echo "Plik 'link' zawiera dla http://rdir.pl/link zawartosc linku" > "$RDIR"/"$README"
fi

blip_echo ""
blip_echo "Pobieram bliplog dla uzytkownika $U"
blip_echo ""

# tymczasowy plik
TMPF="tmp-$$-$RANDOM.tmp"

# pobieramy cokolwiek
if ! wget $WGETOPT -U "$UAGENT" --header "$H1" --header "$H2" --header "$H3" \
     -a "$LOG" -O "$TMPF" \
     "$URLAPI"/"$URLARCH"/"$YNOW"/"$MNOW"'?offset=0&limit=1' ; then 
  blip_fatal "Nie umiem pobrac archiwum uzytkownika: '$U'"
fi
rm -f "$TMPF"

# pobranie avatara (wykomentowane sprawdzanie, czy juz wczesniej pobrany)
AVATARF="$DATA"/"avatar-$U.txt"
AVATARI="$DATA"/"avatar-$U.jpg"
#if [ ! -f "$AVATARF" ] ; then
  if ! wget $WGETOPT -U "$UAGENT" --header "$H1" --header "$H2" --header "$H3" \
        -a "$LOG" -O "$TMPF" \
        "$URLAPI"/"users"/"$U"/"avatar"
  then
    blip_error "nie udalo sie pobrac danych avatara $U"
  else #  elif [ ! -f "$AVATARI" ] ; then
    mv "$TMPF" "$AVATARF"
    AVATARURL="$(cat $AVATARF | sed 's/^.*\"url\":\"\([^\"]*\)\".*$/\1/g')"
    if ! wget $WGETOPT -U "$UAGENT" \
          -a "$LOG" -O "$TMPF" \
          "$AVATARURL"
    then
      blip_error "nie udalo sie pobrac avatara $U"
    else
      mv "$TMPF" "$AVATARI"
      blip_echo "Pobralem avatar $U"
    fi
  fi  
#else
#  blip_echo "Juz mam avatar $U"
#fi

# lista plikow do przejrzenia pod katem RDIR
LRDIR="tmp-lrdir-$$-$RANDOM.tmp" ; touch "$LRDIR"

# jesli to pierwszy raz RDIR, to budujemy liste z obecnych blipniec
if [ "$NOWYRDIR" = "T" ] ; then
  blip_echo "Bede przegladac tez poprzednio pobrane bliniecia szukajac linkow rdir."
  blip_echo ""
  find "$DATA" -type f -name blip-"$U"-\*.txt >> "$LRDIR"
fi

# iteracja po latach
for y in $(seq $YSTART $YNOW) ; do

  # po miesiacach
  for m in $(seq -w 1 12) ; do 
  
   # tag w notatkach dla tego miesiaca - oznaczenie, ze tu bylismy
   TAG="$NOTES"/"$U"-"$y"-"$m"
    
   # czy wczytac ten miesiac? (ten if obejmuje cale wnetrze petli m)
   if [ "$FORCEFULL" = "T" ] || [ ! -f "$TAG" ] || [ -f "$TAG"."$OSTATNI" ] ; then
    
    # czy byl blad i trzeba bedzie ten miesiac kiedys ponownic?
    PONOWIC="N"
    
    # oznaczamy, ze tu bylismy
    touch "$TAG"
    
    # oznaczamy miesiac jako niezamkniety jeszcze, brudny
    touch "$TAG"."$OSTATNI" 
    
    # folder na wyniki z tego miesiaca
    DIR="$DATA"/"$y"/"$m"
    
    # offset - od ktorego blipniecia w miesiacu pobrac
    o=0
    
    # czy przerwac petle ponizej ("T")
    stop="N"
    
    while [ "$stop" != "T" ] ; do 
  
      # informacja na ekranie gdzie jestesmy
      blip_echo_n "$y-$m-$(printf %0"$CNT"i $o) "
      
      # plik na paczke blipniec
      CNAZWA=tmp-blip-$U-archives-$y-$m-$(printf %0"$CNT"i $o)-$$-$(printf %05i $RANDOM).dat
      
      # czy juz jest taki
      if [ -f "$CNAZWA" ] ; then      
        blip_fatal "nie wierze w to, po prostu" 42
      fi
        
      # pobieram paczke blipniec
      if ! wget $WGETOPT -U "$UAGENT" --header "$H1" --header "$H2" --header "$H3" \
           -a "$LOG" -O $CNAZWA \
           "$URLAPI"/"$URLARCH"/"$y"/"$m"'?offset='"$o"'&limit='"$LIMIT"
      then
          blip_fatal "nie udalo sie pobrac $y/$m, offset=$o, limit=$LIMIT"
          PONOWIC="T"
      fi
        
      # nie chcemy zarznac blipa!
      blip_sleep "$SLEEP"
        
      blip_echo_n " pobrany "   
        
      # zapamietujemy pozycje przed iteracja
      o1=$o
         
      # wczytuje plik
      S="$(cat $CNAZWA)"
      
      # usuwam plik
      rm -f "$CNAZWA"

      # ponizej parsujemy S

      # na poczatek usuwamy [] z S
      blip_extract_list 
      
      # wyjmujemy kolejne blipniecia do S1 az S stanie sie puste
      while [ -n "$S" ] ; do

        # tworzymy folder na blipniecia
        mkdir -p "$DIR"

        blip_get_one # wyjmujemy jeden rekord do S1 usuwajac go z S
        #blip_extract_record # usuwamy {} z S1
        
        # ID blipniecia
        BID=$(echo "$S1" | sed 's/^.*\"id\":\([0-9]*\).*$/\1/g')

        # nazwa pliku z pelnym rekordem
        SNAZWA="$DIR"/"blip-$U-$(printf %012i $BID)-full.txt"
        if ! [ -f "$SNAZWA" ] ; then
          # jesli mamy haslo, pobieramy pelny rekord blipniecia (jesli niepobrany)
          if ! [ -z "$ANYP" ] ; then
            if ! wget $WGETOPT -U "$UAGENT" --header "$H1" --header "$H2" --header "$H3" \
                 -a "$LOG" -O "$TMPF" \
                 --user="$ANYU" --password="$ANYP" \
                 --post-data "$WGETOPTSLIKES" \
                 "$URLAPI"/"$URLS"/"$BID" ; then
              if ! wget $WGETOPT -U "$UAGENT" --header "$H1" --header "$H2" --header "$H3" \
                   -a "$LOG" -O "$TMPF" \
                   "$URLAPI"/"$URLS"/"$BID" ; then
                 blip_error "Nie umiem pobrac wiadomosci '$BID' z lajkami czy bez..."
              else              
                mv "$TMPF" "$SNAZWA"
              fi # udalo sie pobranie bez lajkow
            else
              mv "$TMPF" "$SNAZWA"
            fi # udalo sie pobranie z lajkami
          fi
        fi # pobranie rekordu blipniecia
        
        # pole "pictures_attached" (czekamy na true)
        BPIC=$(echo "$S1" | sed 's/^.*\"pictures_attached\":\([a-zA-Z0-9"]*\).*$/\1/g')
        
        # jesli jest obrazek
        if [ "$BPIC" = "true" ] ; then
        
          if ! wget $WGETOPT -U "$UAGENT" --header "$H1" --header "$H2" --header "$H3" \
              -a "$LOG" -O "$TMPF" \
              "$URLAPI"/"updates/$BID/pictures"
          then
            blip_fatal "nie udalo sie pobrac danych obrazka $BID"           
            PONOWIC="T"
          fi
          
          # nazwa pliku na obrazek
          PICNAZWA="$DIR"/"blip-$U-$(printf %012i $BID).jpg"

          # sprawdzam, czy jest niepusty, wget na obrazkach czasem sie nie udawal
          if [ ! -s "$PICNAZWA" ] ; then
          
            # tu zakladam, ze zawsze jest jeden
            PICURL="$(cat $TMPF | sed 's/^.*\"url\":\"\([^\"]*\)\".*$/\1/g')"

            if ! wget $WGETOPT -U "$UAGENT" -a "$LOG" -O $PICNAZWA "$PICURL"
            then
              PONOWIC="T"
              blip_error "nie udalo sie pobrac obrazka $PICURL"
            else  
              blip_echo_n "[]"
            fi
            
          fi
          
          # usuwam plik z danymi obrazka
          rm -f "$TMPF"

        fi
        
        # nazwa pliku na blipniecie
        DNAZWA="$DIR"/"blip-$U-$(printf %012i $BID).txt"
        
        if [ -f "$DNAZWA" ] ; then
          blip_echo_n '-'
        else
          blip_echo_n '+'
          echo "$S1" > "$DNAZWA"
          echo "$DNAZWA" >> "$LRDIR" # dopisujemy do listy do szukania RDIR
        fi

        # numer blipniecia w miesiacu
        o=$(( $o + 1 ))

      done # obrobka jednej paczki blipniec
      
      # jesli dalo mniej niz poprosilismy
      if [ $[ $o1 + $LIMIT ] -gt "$o" ] ; then stop="T" ; fi
      
      blip_echo ''
        
    done # while - pobieranie kolejnych paczek blipniec
    
    # jesli pobralismy akurat biezacy miesiac, ktory trwa, to konczymy obie petle
    if [ "$y" = "$YNOW" ] && [ "$m" = "$MNOW" ] ; then
      break 2
    fi
    
    # jesli nie bylo bledow i przebieg dla tego miesiaca doszedl tu (=udal sie)
    # usuwamy znacznik, ten miesiac mamy w calosci pobrany, nie wrocimy do niego
    if [ "$PONOWIC" = "N" ] && [ -f "$TAG"."$OSTATNI" ] ; then 
      rm -f "$TAG"."$OSTATNI"
    fi
      
   fi # czy pominac ten miesiac

  done # for m - miesiace

done # for y - lata

# jesli jest podane haslo, sprobujemy pobrac listy obserwowanych, wiadomosci prywatne i publiczne
if ! [ -z "$ANYP" ] ; then

  blip_echo "Pobieram liste obserwowanych przez uzytkownika $U"

  if ! wget $WGETOPT -U "$UAGENT" --header "$H1" --header "$H2" --header "$H3" \
       -a "$LOG" -O "$TMPF" \
       --user="$ANYU" --password="$ANYP" \
       "$URLAPI"/"$URLTO" ; then 
    blip_error "Nie umiem pobrac listy obserwowanych przez '$U', login '$ANYU' z haslem '$ANYP'"
  else # ok, pobrane
    mv "$TMPF" "$DATA"/subscriptions-to-"$U".txt
  fi

  blip_echo "Pobieram liste obserwujacych uzytkownika $U"

  if ! wget $WGETOPT -U "$UAGENT" --header "$H1" --header "$H2" --header "$H3" \
       -a "$LOG" -O "$TMPF" \
       --user="$ANYU" --password="$ANYP" \
       "$URLAPI"/"$URLFROM" ; then 
    blip_error "Nie umiem pobrac listy obserwujacych '$U', login '$ANYU' z haslem '$ANYP'"
  else # ok, pobrane
    mv "$TMPF" "$DATA"/subscriptions-from-"$U".txt
  fi

  blip_echo "Pobieram wiadomosci publiczne dla uzytkownika $U"

  # pobieramy cokolwiek, dalej tylko jesli sie uda
  if ! wget $WGETOPT -U "$UAGENT" --header "$H1" --header "$H2" --header "$H3" \
       -a "$LOG" -O "$TMPF" \
       --user="$ANYU" --password="$ANYP" \
       "$URLAPI"/"$URLPUBL"/'0/since?limit=1' ; then 
    blip_error "Nie umiem pobrac wiadomosci publicznych uzytkownika: '$U', login '$ANYU' z haslem '$ANYP'"
  else # ok, mamy dostep
    rm -f "$TMPF"

    mkdir -p "$PUBL"
    if [ ! -f "$PUBL"/"$README" ] ; then
      echo "Pliki z wiadomosciami publicznymi i obrazkami." > "$PUBL"/"$README"
    fi

    # sprawdzmy najwyzszy numer pobranej wiadomosci
    LASTMSG=$(ls "$PUBL"/ | grep "blip-$U-[0-9][0-9]*.txt" | tail -1 | sed 's/^blip-.*-\([0-9][0-9]*\).txt$/\1/g')
    if [ -z "$LASTMSG" ] ; then LASTMSG="0" ; fi
    blip_debug "LASTMSG='$LASTMSG'"

    # czy przerwac petle ponizej ("T")
    stop="N"

    while [ "$stop" != "T" ] ; do

      if ! wget $WGETOPT -U "$UAGENT" --header "$H1" --header "$H2" --header "$H3" \
           -a "$LOG" -O "$TMPF" \
           --user="$ANYU" --password="$ANYP" \
           "$URLAPI"/"$URLPUBL"/"$LASTMSG"/"since" ; then 
        blip_error "Nie umiem pobrac wiadomosci publicznych uzytkownika: '$U', login '$ANYU' z haslem '$ANYP' po wiadomosci '$LASTMSG'"
      elif ! [ -s "$TMPF" ] ; then # plik pusty
        rm -f "$TMPF"
        stop="T"
      else # pobrano paczke wiadomosci

        # dalej kod analogiczny do powyzszego wczytujacego blipniecia
        S="$(cat $TMPF)"
        rm -f "$TMPF"
        blip_extract_list
        while [ -n "$S" ] ; do
          blip_get_one
          BID=$(echo "$S1" | sed 's/^.*\"id\":\([0-9]*\).*$/\1/g')
          if [ "$BID" -gt "$LASTMSG" ] ; then LASTMSG="$BID" ; fi
          if [[ "$S1" == *pictures_path* ]] ; then
            # PPIC=$(echo "$S1" | sed 's/^.*\"pictures_path\":\([\/a-zA-Z0-9"]*\).*$/\1/g')
            if ! wget $WGETOPT -U "$UAGENT" --header "$H1" --header "$H2" --header "$H3" \
                -a "$LOG" -O "$TMPF" \
                "$URLAPI"/"updates/$BID/pictures"
            then
              blip_error "nie udalo sie pobrac danych obrazka $BID"
            else
              PICNAZWA="$PUBL"/"blip-$U-$(printf %012i $BID).jpg"
              PICURL="$(cat $TMPF | sed 's/^.*\"url\":\"\([^\"]*\)\".*$/\1/g')"
              if ! wget $WGETOPT -U "$UAGENT" -a "$LOG" -O $PICNAZWA "$PICURL"
              then
                blip_error "nie udalo sie pobrac obrazka $PICURL"
              else  
                blip_echo_n "[]"
              fi
              rm -f "$TMPF"
            fi
          fi
          DNAZWA="$PUBL"/"blip-$U-$(printf %012i $BID).txt"
          if [ -f "$DNAZWA" ] ; then
            blip_echo_n '-'
          else
            blip_echo_n '+'
            echo "$S1" > "$DNAZWA"
            echo "$DNAZWA" >> "$LRDIR" # dopisujemy do listy do szukania RDIR
          fi

        done # parsowanie pliku z wiadomosciami

        blip_echo ''

      fi # pobranie jednej paczki wiadomosci publicznych

    done # while pobieranie wiadomosci publicznych

  fi # czy umiemy pobierac wiadomosci publiczne

fi

# do tagow i  wiadomosci prywatnych potrzebujemy naszego hasla, nie obcego
if ! [ -z "$P" ] ; then

  blip_echo "Pobieram liste obserwowanych tagow uzytkownika $U"

  if ! wget $WGETOPT -U "$UAGENT" --header "$H1" --header "$H2" --header "$H3" \
       -a "$LOG" -O "$TMPF" \
       --user="$U" --password="$P" \
       "$URLAPI"/"$URLTAGS" ; then 
    blip_error "Nie umiem pobrac listy tagow '$U', login '$U' z haslem '$P'"
  else # ok, pobrane
    mv "$TMPF" "$DATA"/tags-"$U".txt
  fi

  blip_echo "Pobieram liste ignorowanych tagow uzytkownika $U"

  if ! wget $WGETOPT -U "$UAGENT" --header "$H1" --header "$H2" --header "$H3" \
       -a "$LOG" -O "$TMPF" \
       --user="$U" --password="$P" \
       "$URLAPI"/"$URLTAGSI" ; then 
    blip_error "Nie umiem pobrac listy ignorowanych tagow '$U', login '$U' z haslem '$P'"
  else # ok, pobrane
    mv "$TMPF" "$DATA"/tags-ignored-"$U".txt
  fi

  blip_echo "Pobieram wiadomosci prywatne dla uzytkownika $U"

  # pobieramy cokolwiek, dalej tylko jesli sie uda
  if ! wget $WGETOPT -U "$UAGENT" --header "$H1" --header "$H2" --header "$H3" \
       -a "$LOG" -O "$TMPF" \
       --user="$U" --password="$P" \
       "$URLAPI"/"$URLPRIV"/'0?limit=1' ; then 
    blip_error "Nie umiem pobrac wiadomosci prywatnych uzytkownika: '$U' z haslem '$P'"
  else # ok, mamy dostep
    rm -f "$TMPF"

    mkdir -p "$PRIV"
    if [ ! -f "$PRIV"/"$README" ] ; then
      echo "Pliki z wiadomosciami prywatnymi i obrazkami." > "$PRIV"/"$README"
    fi

    # sprawdzmy najwyzszy numer pobranej wiadomosci
    LASTMSG=$(ls "$PRIV"/ | grep "blip-$U-[0-9][0-9]*.txt" | tail -1 | sed 's/^blip-.*-\([0-9][0-9]*\).txt$/\1/g')
    if [ -z "$LASTMSG" ] ; then LASTMSG="0" ; fi
    blip_debug "LASTMSG='$LASTMSG'"

    # czy przerwac petle ponizej ("T")
    stop="N"

    while [ "$stop" != "T" ] ; do

      if ! wget $WGETOPT -U "$UAGENT" --header "$H1" --header "$H2" --header "$H3" \
           -a "$LOG" -O "$TMPF" \
           --user="$U" --password="$P" \
           "$URLAPI"/"$URLPRIV"/"$LASTMSG" ; then 
        blip_error "Nie umiem pobrac wiadomosci prywatnych uzytkownika: '$U' z haslem '$P' po wiadomosci '$LASTMSG'"
      elif ! [ -s "$TMPF" ] ; then # plik pusty
        rm -f "$TMPF"
        stop="T"
      else # pobrano paczke wiadomosci

        # dalej kod analogiczny do powyzszego wczytujacego blipniecia
        S="$(cat $TMPF)"
        rm -f "$TMPF"
        blip_extract_list
        while [ -n "$S" ] ; do
          blip_get_one
          BID=$(echo "$S1" | sed 's/^.*\"id\":\([0-9]*\).*$/\1/g')
          if [ "$BID" -gt "$LASTMSG" ] ; then LASTMSG="$BID" ; fi
          if [[ "$S1" == *pictures_path* ]] ; then
            # PPIC=$(echo "$S1" | sed 's/^.*\"pictures_path\":\([\/a-zA-Z0-9"]*\).*$/\1/g')
            if ! wget $WGETOPT -U "$UAGENT" --header "$H1" --header "$H2" --header "$H3" \
                -a "$LOG" -O "$TMPF" \
                --user="$U" --password="$P" \
                "$URLAPI"/"updates/$BID/pictures"
            then
              blip_error "nie udalo sie pobrac danych obrazka $BID"
            else
              blip_cookie
              PICNAZWA="$PRIV"/"blip-$U-$(printf %012i $BID).jpg"
              PICURL="$(cat $TMPF | sed 's/^.*\"url\":\"\([^\"]*\)\".*$/\1/g')"
              if ! wget --load-cookies "$COOKIES" $WGETOPT -U "$UAGENT" -a "$LOG" -O $PICNAZWA --user="$U" --password="$P" "$PICURL"
              then
                blip_error "nie udalo sie pobrac obrazka $PICURL"
              elif fgrep -q DOCTYPE $PICNAZWA ; then
                rm -f $PICNAZWA
                blip_error "nie udalo sie pobrac obrazka $PICURL (brak sesji)"
              else  
                blip_echo_n "[]"
              fi
              rm -f "$TMPF"
            fi
          fi
          DNAZWA="$PRIV"/"blip-$U-$(printf %012i $BID).txt"
          if [ -f "$DNAZWA" ] ; then
            blip_echo_n '-'
          else
            blip_echo_n '+'
            echo "$S1" > "$DNAZWA"
            echo "$DNAZWA" >> "$LRDIR" # dopisujemy do listy do szukania RDIR
          fi

        done # parsowanie pliku z wiadomosciami

        blip_echo ''

      fi # pobranie jednej paczki wiadomosci prywatnych

    done # while pobieranie wiadomosci prywatnych

  fi # czy umiemy pobierac wiadomosci prywatne

fi # czy jest podane haslo

# szukamy linkow rdir
if [ -s "$LRDIR" ] ; then
  blip_echo_n "Pobieramy jeszcze linki rdir: "
  cat "$LRDIR" | 
  while read F ; do # sklejamy wszystkie wpisy do przejrzenia
    if [ -r "$F" ] ; then
      cat "$F" 
    else
      blip_fatal "Nie wiem dlaczego nie widze pliku '$F'"
    fi
  done | \
  sed 's/\(http:\/\/rdir\.pl\/[0-9a-zA-Z]*\)/\|\1\|/g' | \
  tr '|' '\n' | \
  grep '^http://rdir\.pl/[0-9a-zA-Z]*$' | \
  sort | uniq | sed 's/^http:\/\/rdir\.pl\/\(.*\)$/\1/g' | \
  while read F ; do # pobieram link
    if [ ! -f "$RDIR"/"$F" ] ; then
      if ! wget $WGETOPT -U "$UAGENT" --header "$H1" --header "$H2" --header "$H3" \
         -a "$LOG" -O "$RDIR"/"$F" \
            "$URLAPI"/"shortlinks"/"$F"
      then
        blip_error "nie udalo sie pobrac danych linku http://rdir.pl/$F"
      fi  
      blip_echo_n '+'
    else
      blip_echo_n '-'
    fi
  done
  blip_echo ''
fi

# usuwamy liste
if [ -f "$LRDIR" ] ; then rm -f "$LRDIR" ; fi

# usuwamy ciasteczka
if [ -f "$COOKIES" ] ; then rm -f "$COOKIES" ; fi

# zaszlosc z wersji 1.0
if [ -d "$CACHE" ] ; then 
  blip_error "katalog CACHE mozna skasowac, nie uzywam go"
fi
