# Przypadki Testowe: Recurring Expenses

## TC-REC-001: Automatyczne wygenerowanie wydatku cyklicznego w dniu `next_run`
**Opis:** Weryfikacja, że aktywny cykliczny wydatek zostaje przetworzony przez scheduler i tworzy nowy wpis wydatku w grupie.

**Warunki wstępne:**
- Istnieje grupa z co najmniej 2 członkami.
- Użytkownik A jest członkiem grupy i utworzył recurring expense:
  - `description`: "Netflix"
  - `amount`: `60.00`
  - `currency`: `PLN`
  - `split_type`: `EQUAL`
  - `interval`: `MONTHLY`
  - `next_run`: dzisiejsza data
  - `is_active`: `true`
- Scheduler (`process_recurring_expenses`) jest uruchomiony dla dzisiejszej daty.

**Kroki:**
1. Uruchom przetwarzanie recurring expenses (job schedulera).
2. Odczytaj listę wydatków dla tej grupy.
3. Odczytaj rekord recurring expense po wykonaniu joba.
4. (Opcjonalnie) nasłuchuj kanału WebSocket grupy.

**Oczekiwany rezultat:**
- Powstał nowy wydatek w grupie z opisem prefiksowanym jako `[Recurring] Netflix`.
- Kwota i waluta wygenerowanego wydatku to odpowiednio `60.00 PLN`.
- Splity zostały utworzone dla wszystkich aktualnych członków grupy.
- Pole `next_run` w recurring expense zostało przesunięte o 1 miesiąc.
- (Jeśli WebSocket aktywny) wysłano event typu `recurring_expense_generated`.

**Priorytet:** Wysoki
**Typ testu:** Integracyjny / API + scheduler

## TC-REC-002: Dezaktywacja recurring expense zatrzymuje dalsze generowanie
**Opis:** Weryfikacja, że po dezaktywacji wpisu cyklicznego scheduler nie tworzy już kolejnych wydatków z tego szablonu.

**Warunki wstępne:**
- Istnieje grupa z co najmniej 2 członkami.
- Istnieje aktywny recurring expense z `next_run` ustawionym na dzisiaj.
- Użytkownik wykonujący operację jest członkiem grupy.

**Kroki:**
1. Wywołaj endpoint deaktywacji recurring expense (`DELETE /groups/{group_id}/recurring-expenses/{recurring_id}`).
2. Zweryfikuj, że wpis recurring ma ustawione `is_active = false`.
3. Uruchom job schedulera (`process_recurring_expenses`).
4. Odczytaj listę wydatków grupy po zakończeniu joba.

**Oczekiwany rezultat:**
- Endpoint zwraca status `204 No Content`.
- Wpis recurring jest nieaktywny.
- Scheduler nie generuje nowego wydatku z dezaktywowanego wpisu.

**Priorytet:** Wysoki
**Typ testu:** Integracyjny / API + scheduler

## TC-REC-003: Brak członkostwa w grupie blokuje operacje recurring
**Opis:** Weryfikacja kontroli dostępu dla użytkownika, ktory nie nalezy do grupy.

**Warunki wstępne:**
- Istnieje grupa G.
- Użytkownik B nie jest członkiem grupy G.

**Kroki:**
1. Jako użytkownik B wywołaj utworzenie recurring (`POST /groups/{group_id}/recurring-expenses`).
2. Jako użytkownik B wywołaj listowanie recurring (`GET /groups/{group_id}/recurring-expenses`).
3. Jako użytkownik B wywołaj deaktywację istniejącego recurring (`DELETE /groups/{group_id}/recurring-expenses/{recurring_id}`).

**Oczekiwany rezultat:**
- Każda operacja jest odrzucona statusem `403 Forbidden`.
- Komunikat błędu wskazuje brak członkostwa (`You are not a member of this group`).

**Priorytet:** Wysoki
**Typ testu:** API / Autoryzacja

## TC-REC-004: Tworzenie recurring dla nieistniejącej grupy
**Opis:** Weryfikacja obsługi przypadku, gdy użytkownik próbuje utworzyć recurring expense dla grupy, ktora nie istnieje.

**Warunki wstępne:**
- Użytkownik jest poprawnie uwierzytelniony.
- `group_id` przekazany w żądaniu nie istnieje w bazie.

**Kroki:**
1. Wywołaj `POST /groups/{group_id}/recurring-expenses` z poprawnym payloadem dla nieistniejącej grupy.

**Oczekiwany rezultat:**
- Endpoint zwraca `404 Not Found`.
- Treść błędu: `Group not found`.
- W bazie nie powstaje nowy wpis recurring.

**Priorytet:** Sredni
**Typ testu:** API / Walidacja zasobow

## TC-REC-005: Brak due recurring expenses nie tworzy nowych wydatkow
**Opis:** Weryfikacja, że scheduler konczy działanie bez skutkow ubocznych, gdy nie ma aktywnych pozycji do uruchomienia w danym dniu.

**Warunki wstępne:**
- W systemie brak recurring z `next_run <= dzisiaj` i `is_active = true`.

**Kroki:**
1. Uruchom job schedulera (`process_recurring_expenses`).
2. Odczytaj liczbe wydatkow przed i po uruchomieniu joba.
3. (Opcjonalnie) sprawdz logi / websocket dla eventow recurring.

**Oczekiwany rezultat:**
- Nie powstaje zaden nowy wpis `Expense`.
- Nie są wysyłane eventy `recurring_expense_generated`.
- Job konczy się poprawnie bez wyjątku.

**Priorytet:** Sredni
**Typ testu:** Integracyjny / scheduler

## TC-REC-006: Poprawne przesuwanie `next_run` dla WEEKLY i YEARLY
**Opis:** Weryfikacja, że po wygenerowaniu wydatku data kolejnego uruchomienia jest poprawnie liczona dla roznych interwałow.

**Warunki wstępne:**
- Istnieją dwa aktywne recurring expenses w tej samej lub roznych grupach:
  - REC-W (`interval = WEEKLY`, `next_run = 2026-03-18`)
  - REC-Y (`interval = YEARLY`, `next_run = 2026-03-18`)
- Oba wpisy sa due na dzisiaj.

**Kroki:**
1. Uruchom `process_recurring_expenses`.
2. Odczytaj oba rekordy recurring po wykonaniu joba.

**Oczekiwany rezultat:**
- Dla REC-W pole `next_run` zostaje ustawione na `2026-03-25`.
- Dla REC-Y pole `next_run` zostaje ustawione na `2027-03-18`.
- Dla obu wpisow wygenerowano po jednym nowym wydatku.

**Priorytet:** Sredni
**Typ testu:** Integracyjny / scheduler + logika dat


