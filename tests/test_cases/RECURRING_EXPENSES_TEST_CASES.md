# Przypadki Testowe: Recurring Expenses

## TC-REC-001: Automatyczne wygenerowanie wydatku cyklicznego w dniu `next\_run`

**Opis:** Weryfikacja, że aktywny cykliczny wydatek zostaje przetworzony przez scheduler i tworzy nowy wpis wydatku w grupie.

**Warunki wstępne:**

* Istnieje grupa z co najmniej 2 członkami.
* Użytkownik A jest członkiem grupy i utworzył recurring expense:

  * `description`: "Netflix"
  * `amount`: `60.00`
  * `currency`: `PLN`
  * `split\_type`: `EQUAL`
  * `interval`: `MONTHLY`
  * `next\_run`: dzisiejsza data
  * `is\_active`: `true`
* Scheduler (`process\_recurring\_expenses`) jest uruchomiony dla dzisiejszej daty.

**Kroki:**

1. Uruchom przetwarzanie recurring expenses (job schedulera).
2. Odczytaj listę wydatków dla tej grupy.
3. Odczytaj rekord recurring expense po wykonaniu joba.
4. (Opcjonalnie) nasłuchuj kanału WebSocket grupy.

**Oczekiwany rezultat:**

* Powstał nowy wydatek w grupie z opisem prefiksowanym jako `\[Recurring] Netflix`.
* Kwota i waluta wygenerowanego wydatku to odpowiednio `60.00 PLN`.
* Splity zostały utworzone dla wszystkich aktualnych członków grupy.
* Pole `next\_run` w recurring expense zostało przesunięte o 1 miesiąc.
* (Jeśli WebSocket aktywny) wysłano event typu `recurring\_expense\_generated`.


**Typ testu:** Integracyjny / API + scheduler

## TC-REC-002: Dezaktywacja recurring expense zatrzymuje dalsze generowanie

**Opis:** Weryfikacja, że po dezaktywacji wpisu cyklicznego scheduler nie tworzy już kolejnych wydatków z tego szablonu.

**Warunki wstępne:**

* Istnieje grupa z co najmniej 2 członkami.
* Istnieje aktywny recurring expense z `next\_run` ustawionym na dzisiaj.
* Użytkownik wykonujący operację jest członkiem grupy.

**Kroki:**

1. Wywołaj endpoint deaktywacji recurring expense (`DELETE /groups/{group\_id}/recurring-expenses/{recurring\_id}`).
2. Zweryfikuj, że wpis recurring ma ustawione `is\_active = false`.
3. Uruchom job schedulera (`process\_recurring\_expenses`).
4. Odczytaj listę wydatków grupy po zakończeniu joba.

**Oczekiwany rezultat:**

* Endpoint zwraca status `204 No Content`.
* Wpis recurring jest nieaktywny.
* Scheduler nie generuje nowego wydatku z dezaktywowanego wpisu.



**Typ testu:** Integracyjny / API + scheduler

## TC-REC-003: Brak członkostwa w grupie blokuje operacje recurring

**Opis:** Weryfikacja kontroli dostępu dla użytkownika, ktory nie nalezy do grupy.

**Warunki wstępne:**

* Istnieje grupa G.
* Użytkownik B nie jest członkiem grupy G.

**Kroki:**

1. Jako użytkownik B wywołaj utworzenie recurring (`POST /groups/{group\_id}/recurring-expenses`).
2. Jako użytkownik B wywołaj listowanie recurring (`GET /groups/{group\_id}/recurring-expenses`).
3. Jako użytkownik B wywołaj deaktywację istniejącego recurring (`DELETE /groups/{group\_id}/recurring-expenses/{recurring\_id}`).

**Oczekiwany rezultat:**

* Każda operacja jest odrzucona statusem `403 Forbidden`.
* Komunikat błędu wskazuje brak członkostwa (`You are not a member of this group`).


**Typ testu:** API / Autoryzacja

## TC-REC-004: Tworzenie recurring dla nieistniejącej grupy

**Opis:** Weryfikacja obsługi przypadku, gdy użytkownik próbuje utworzyć recurring expense dla grupy, ktora nie istnieje.

**Warunki wstępne:**

* Użytkownik jest poprawnie uwierzytelniony.
* `group\_id` przekazany w żądaniu nie istnieje w bazie.

**Kroki:**

1. Wywołaj `POST /groups/{group\_id}/recurring-expenses` z poprawnym payloadem dla nieistniejącej grupy.

**Oczekiwany rezultat:**

* Endpoint zwraca `404 Not Found`.
* Treść błędu: `Group not found`.
* W bazie nie powstaje nowy wpis recurring.


**Typ testu:** API / Walidacja zasobow

## TC-REC-005: Brak due recurring expenses nie tworzy nowych wydatkow

**Opis:** Weryfikacja, że scheduler konczy działanie bez skutkow ubocznych, gdy nie ma aktywnych pozycji do uruchomienia w danym dniu.

**Warunki wstępne:**

* W systemie brak recurring z `next\_run <= dzisiaj` i `is\_active = true`.

**Kroki:**

1. Uruchom job schedulera (`process\_recurring\_expenses`).
2. Odczytaj liczbe wydatkow przed i po uruchomieniu joba.
3. (Opcjonalnie) sprawdz logi / websocket dla eventow recurring.

**Oczekiwany rezultat:**

* Nie powstaje zaden nowy wpis `Expense`.
* Nie są wysyłane eventy `recurring\_expense\_generated`.
* Job konczy się poprawnie bez wyjątku.


**Typ testu:** Integracyjny / scheduler

## TC-REC-006: Poprawne przesuwanie `next\_run` dla WEEKLY i YEARLY

**Opis:** Weryfikacja, że po wygenerowaniu wydatku data kolejnego uruchomienia jest poprawnie liczona dla roznych interwałow.

**Warunki wstępne:**

* Istnieją dwa aktywne recurring expenses w tej samej lub roznych grupach:

  * REC-W (`interval = WEEKLY`, `next\_run = 2026-03-18`)
  * REC-Y (`interval = YEARLY`, `next\_run = 2026-03-18`)
* Oba wpisy sa due na dzisiaj.

**Kroki:**

1. Uruchom `process\_recurring\_expenses`.
2. Odczytaj oba rekordy recurring po wykonaniu joba.

**Oczekiwany rezultat:**

* Dla REC-W pole `next\_run` zostaje ustawione na `2026-03-25`.
* Dla REC-Y pole `next\_run` zostaje ustawione na `2027-03-18`.
* Dla obu wpisow wygenerowano po jednym nowym wydatku.


**Typ testu:** Integracyjny / scheduler + logika dat

## TC-REC-007: Dezaktywacja z nieistniejacym `recurring\_id`

**Opis:** Weryfikacja, ze API poprawnie zwraca blad, gdy probujemy usunac wpis recurring, ktory nie istnieje w danej grupie.

**Warunki wstępne:**

* Uzytkownik jest poprawnie uwierzytelniony i jest czlonkiem grupy.
* `group\_id` istnieje.
* `recurring\_id` nie istnieje lub nie nalezy do tej grupy.

**Kroki:**

1. Wywolaj `DELETE /groups/{group\_id}/recurring-expenses/{recurring\_id}` dla nieistniejacego ID.

**Oczekiwany rezultat:**

* Endpoint zwraca `404 Not Found`.
* Tresc bledu: `Recurring expense not found`.
* Zadna inna pozycja recurring nie zostaje zmodyfikowana.


**Typ testu:** API / Walidacja zasobow

## TC-REC-008: Scheduler pomija recurring bez czlonkow grupy

**Opis:** Weryfikacja zachowania schedulera, gdy istnieje due recurring, ale zapytanie o czlonkow grupy zwraca pusta liste.

**Warunki wstępne:**

* Istnieje aktywny recurring expense z `next\_run <= dzisiaj`.
* Dla `group\_id` recurring brak wpisow w `UserGroup` (lista czlonkow jest pusta).

**Kroki:**

1. Uruchom `process\_recurring\_expenses`.
2. Odczytaj wydatki dla tej grupy.
3. Odczytaj rekord recurring po zakonczeniu joba.

**Oczekiwany rezultat:**

* Scheduler nie tworzy nowego `Expense`.
* Nie sa tworzone zadne `ExpenseSplit`.
* Pole `next\_run` pozostaje bez zmian (rekord zostal pominiety).
* Job konczy sie bez nieobsluzonego wyjatku.


**Typ testu:** Integracyjny / scheduler

## TC-REC-009: Rollback transakcji przy bledzie podczas przetwarzania schedulera

**Opis:** Weryfikacja, ze w przypadku bledu runtime podczas `process\_recurring\_expenses` dane nie zostaja zapisane czesciowo.

**Warunki wstępne:**

* Istnieje co najmniej jeden due recurring expense.
* Srodowisko testowe pozwala zasymulowac blad (np. wyjatek przy zapisie splitu lub przy broadcast).

**Kroki:**

1. Uruchom `process\_recurring\_expenses` z kontrolowanym bledem w trakcie przetwarzania.
2. Po zakonczeniu sprawdz stan tabel `Expense`, `ExpenseSplit` i recurring.

**Oczekiwany rezultat:**

* Proces loguje blad i wykonuje rollback transakcji.
* Nie ma czesciowo zapisanych nowych wydatkow/splitow.
* `next\_run` dla przetwarzanego recurring nie zostaje przesuniety.


**Typ testu:** Integracyjny / odporność na bledy

## TC-REC-010: Domyslna waluta i mapowanie pol odpowiedzi create/list

**Opis:** Weryfikacja, ze API recurring poprawnie uzupelnia domyslna walute oraz zwraca wymagane pola (`creator\_name`, `currency`) po utworzeniu i listowaniu.

**Warunki wstępne:**

* Uzytkownik jest czlonkiem grupy i ma ustawione `display\_name`.
* Payload `POST` nie zawiera pola `currency`.

**Kroki:**

1. Wywolaj `POST /groups/{group\_id}/recurring-expenses` bez `currency`.
2. Sprawdz odpowiedz create.
3. Wywolaj `GET /groups/{group\_id}/recurring-expenses`.
4. Sprawdz rekord na liscie.

**Oczekiwany rezultat:**

* W odpowiedzi `POST` pole `currency` ma wartosc `PLN`.
* Pole `creator\_name` odpowiada `display\_name` zalogowanego uzytkownika.
* Ten sam rekord jest widoczny w odpowiedzi `GET` z tym samym `id`, `currency` i `creator\_name`.


**Typ testu:** API / Kontrakt odpowiedzi

