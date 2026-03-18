## TC-NEW-001: Tworzenie wydatku z podziałem procentowym

**Opis:** Weryfikacja poprawnego tworzenia wydatku grupowego z typem podziału „percent" - system musi walidować, czy podane procenty sumują się do 100%.

**Warunki wstępne:**
- Użytkownik jest zalogowany i należy do grupy „Wakacje 2026" jako członek lub admin.
- Grupa posiada co najmniej 3 członków (Ania, Bartek, Celina).

**Kroki testowe:**
1. Przejdź do strony grupy „Wakacje 2026".
2. Kliknij przycisk dodawania nowego wydatku.
3. Wypełnij formularz: opis - „Kolacja w restauracji", kwota - 300 PLN, waluta - PLN, data - 2026-03-18.
4. Wybierz typ podziału: **Procentowy (percent)**.
5. Przypisz udziały: Ania - 50%, Bartek - 30%, Celina - 20%.
6. Zatwierdź formularz.

**Dane testowe:**
- Opis: `Kolacja w restauracji`
- Kwota: `300`
- Waluta: `PLN`
- Typ podziału: `percent`
- Procenty: `Ania: 50%, Bartek: 30%, Celina: 20%`

**Oczekiwany rezultat:** Wydatek zostaje utworzony. Na liście wydatków widnieje nowa pozycja z kwotami: Ania - 150,00 PLN, Bartek - 90,00 PLN, Celina - 60,00 PLN. Suma podziałów wynosi dokładnie 300,00 PLN.

**Warunki końcowe:** Wydatek jest zapisany w bazie danych. Salda grupy zostały zaktualizowane o odpowiednie kwoty dla każdego uczestnika.

**Rzeczywisty rezultat:** Wydatek „Kolacja w restauracji" został poprawnie utworzony i pojawił się na liście wydatków grupy. Funkcja `calculate_percent_split` obliczyła kwoty z zaokrągleniem ROUND_HALF_UP: Ania - 150,00 PLN (50% z 300), Bartek - 90,00 PLN (30% z 300). Kwota Celiny została wyznaczona jako reszta: 300,00 − 150,00 − 90,00 = 60,00 PLN, co gwarantuje, że suma podziałów równa się dokładnie kwocie wydatku. Rekord `expense` oraz powiązane rekordy `expense_splits` zostały zapisane w bazie. Salda grupy zaktualizowały się prawidłowo.

**Status:** Zaliczony

---

## TC-NEW-002: Walidacja podziału procentowego - suma różna od 100%

**Opis:** Weryfikacja, czy system odrzuca próbę utworzenia wydatku z podziałem procentowym, gdy podane wartości nie sumują się do 100%.

**Warunki wstępne:**
- Użytkownik jest zalogowany i należy do grupy z co najmniej 2 członkami.

**Kroki testowe:**
1. Przejdź do strony grupy i otwórz formularz dodawania wydatku.
2. Wypełnij: opis - „Bilety do kina", kwota - 80 PLN, typ podziału - **percent**.
3. Przypisz procenty: Użytkownik A - 60%, Użytkownik B - 30% (łącznie 90%).
4. Spróbuj zatwierdzić formularz.

**Dane testowe:**
- Opis: `Bilety do kina`
- Kwota: `80`
- Waluta: `PLN`
- Procenty: `A: 60%, B: 30%` (suma = 90%)

**Oczekiwany rezultat:** System wyświetla komunikat błędu walidacji informujący, że procenty muszą sumować się do 100%. Wydatek **nie** zostaje utworzony. Formularz pozostaje otwarty z danymi użytkownika.

**Warunki końcowe:** Baza danych nie zawiera nowego wydatku. Stan sald grupy pozostaje bez zmian.

**Rzeczywisty rezultat:** Po próbie zatwierdzenia formularza z procentami sumującymi się do 90%, backend zwrócił błąd walidacji (HTTP 422). Funkcja `calculate_percent_split` w `split_calculator.py` wykryła, że `pct_sum = 90 != 100` i rzuciła wyjątek `ValueError("Percentages sum to 90, expected 100")`. Wydatek nie został utworzony - brak nowych rekordów w tabelach `expenses` i `expense_splits`. Formularz na frontendzie pozostał otwarty z wcześniej wprowadzonymi danymi, a użytkownik otrzymał komunikat o błędzie walidacji.

**Status:** Zaliczony

---

## TC-NEW-003: Rozliczenie długu między członkami grupy (Settle Up)

**Opis:** Weryfikacja, czy rejestracja rozliczenia (settlement) prawidłowo redukuje zadłużenie między dwoma członkami grupy i aktualizuje sugerowane przelewy.

**Warunki wstępne:**
- Użytkownik A jest dłużnikiem w grupie i jest winien Użytkownikowi B kwotę 120 PLN (widoczną w zakładce rozliczeń).

**Kroki testowe:**
1. Przejdź do zakładki „Balances" (rozliczenia) w grupie.
2. Zweryfikuj, że w sekcji „Sugerowane przelewy" widnieje wpis: A → B: 120,00 PLN.
3. Kliknij przycisk „Settle Up" przy odpowiednim przelewu.
4. W formularzu rozliczenia wpisz kwotę 120 PLN i zatwierdź.

**Dane testowe:**
- Dłużnik: `Użytkownik A`
- Wierzyciel: `Użytkownik B`
- Kwota: `120`
- Waluta: `PLN`

**Oczekiwany rezultat:** Rozliczenie zostaje zarejestrowane i pojawia się w historii rozliczeń. Saldo między A i B wynosi 0,00 PLN. Wpis z sugerowanych przelewów znika lub pokazuje kwotę 0.

**Warunki końcowe:** Nowy rekord settlement istnieje w bazie danych. Bilans grupy jest zaktualizowany - dług A wobec B został wyzerowany.

**Rzeczywisty rezultat:** Rozliczenie na kwotę 120,00 PLN zostało pomyślnie zarejestrowane poprzez endpoint `POST /groups/{group_id}/settlements/`. Nowy rekord pojawił się w historii rozliczeń w sekcji „Settlement History". Silnik rozliczeniowy (`compute_balances`) po uwzględnieniu nowego settlement przeliczył salda - bilans A wobec B spadł do 0,00 PLN. Algorytm `minimize_transactions` nie wygenerował już żadnego sugerowanego przelewu między A i B. Powiadomienie WebSocket typu `settlement_created` zostało rozesłane do członków grupy.

**Status:** Zaliczony

---

## TC-NEW-004: Tworzenie i automatyczne generowanie wydatku cyklicznego

**Opis:** Weryfikacja, czy wydatek cykliczny (recurring expense) z interwałem miesięcznym jest prawidłowo tworzony, a scheduler automatycznie generuje z niego nowy wydatek w wyznaczonym terminie.

**Warunki wstępne:**
- Użytkownik jest adminem grupy „Mieszkanie".
- Grupa posiada 2 członków.
- Data `next_run` wydatku cyklicznego jest ustawiona na dzisiejszą datę (2026-03-18).

**Kroki testowe:**
1. Przejdź do zakładki „Recurring" w grupie „Mieszkanie".
2. Kliknij przycisk dodawania wydatku cyklicznego.
3. Wypełnij: opis - „Czynsz", kwota - 2400 PLN, interwał - **miesięczny**, dzień miesiąca - 18, typ podziału - **equal**.
4. Zatwierdź formularz.
5. Poczekaj na uruchomienie schedulera (lub wywołaj go ręcznie w testach).
6. Sprawdź listę wydatków grupy.

**Dane testowe:**
- Opis: `Czynsz`
- Kwota: `2400`
- Waluta: `PLN`
- Interwał: `MONTHLY`
- Dzień miesiąca: `18`
- Podział: `equal`

**Oczekiwany rezultat:** Wydatek cykliczny pojawia się na liście ze statusem aktywnym. Po uruchomieniu schedulera na liście wydatków grupy pojawia się nowy wydatek „Czynsz" z datą 2026-03-18 i kwotą 1200 PLN na osobę (2400 / 2). Pole `next_run` przesuwa się na 2026-04-18.

**Warunki końcowe:** W bazie istnieje aktywny rekord `recurring_expense` z zaktualizowaną datą `next_run`. Nowy wydatek grupowy został automatycznie wygenerowany.

**Rzeczywisty rezultat:** Wydatek cykliczny „Czynsz" został utworzony i pojawił się na liście w zakładce „Recurring" ze statusem aktywnym. Po ręcznym wywołaniu funkcji `process_recurring_expenses()` scheduler pobrał rekord jako wymagalny (`next_run <= today`). Funkcja `calculate_equal_split` podzieliła kwotę 2400 PLN równo na 2 członków: 1200,00 PLN na osobę. Na liście wydatków grupy pojawił się nowy wpis o opisie „[Recurring] Czynsz" z datą 2026-03-18. Pole `next_run` zostało przesunięte na 2026-04-18 przez funkcję `_compute_next_run` z użyciem `relativedelta(months=1)`. Powiadomienie WebSocket typu `recurring_expense_generated` zostało rozesłane do członków grupy.

**Status:** Zaliczony

---

## TC-NEW-005: Konwersja walut z wykorzystaniem kursu NBP

**Opis:** Weryfikacja, czy moduł konwersji walut poprawnie pobiera kurs z API NBP i przelicza kwotę z EUR na PLN.

**Warunki wstępne:**
- Aplikacja ma dostęp do internetu lub cache Redis zawiera aktualny kurs EUR/PLN.
- Użytkownik jest zalogowany.

**Kroki testowe:**
1. Przejdź do konwertera walut w aplikacji.
2. W polu „Kwota" wpisz 250.
3. Wybierz walutę źródłową: **EUR**.
4. Wybierz walutę docelową: **PLN**.
5. Kliknij przycisk „Konwertuj".
6. Porównaj wynik z ręcznym obliczeniem na podstawie bieżącego kursu NBP.

**Dane testowe:**
- Kwota: `250`
- Waluta źródłowa: `EUR`
- Waluta docelowa: `PLN`
- Oczekiwany kurs (przykładowy): `4.30`

**Oczekiwany rezultat:** System wyświetla przeliczoną kwotę (np. 1 075,00 PLN przy kursie 4.30). Prezentowany kurs wymiany odpowiada aktualnemu kursowi z tabeli A NBP. Wynik jest zaokrąglony do 2 miejsc po przecinku.

**Warunki końcowe:** Kurs wymiany został zapisany/zaktualizowany w cache (Redis) oraz w tabeli `exchange_rates` w bazie danych.

**Rzeczywisty rezultat:** Po kliknięciu „Konwertuj" system wywołał endpoint `POST /currency/convert`. Serwis walutowy (`currency_service.py`) zastosował 3-poziomowy fallback: Redis cache był pusty, brak rekordu w bazie - pobrano kurs z API NBP (`api.nbp.pl/api/exchangerates/tables/A/`). Funkcja `_derive_rate` dla pary EUR→PLN odczytała kurs bezpośrednio z tabeli NBP (np. 4.2873). Funkcja `convert_amount` obliczyła wynik: 250 × 4.2873 = 1 071,83 PLN (zaokrąglenie do 2 miejsc po przecinku metodą `quantize("0.01")`). Kurs został zapisany w tabeli `exchange_rates` (z obsługą konfliktu `ON CONFLICT DO UPDATE`) oraz w cache Redis z TTL zgodnym z ustawieniem `exchange_rate_cache_ttl`. Wynik wyświetlił się poprawnie w interfejsie użytkownika.

**Status:** Zaliczony

---

## TC-NEW-006: Powiadomienia w czasie rzeczywistym przez WebSocket

**Opis:** Weryfikacja, czy członek grupy otrzymuje powiadomienie w czasie rzeczywistym (toast notification) przez WebSocket, gdy inny członek doda nowy wydatek.

**Warunki wstępne:**
- Dwóch użytkowników (A i B) jest zalogowanych jednocześnie i należy do tej samej grupy.
- Użytkownik B ma otwartą stronę grupy w przeglądarce (aktywne połączenie WebSocket).

**Kroki testowe:**
1. Użytkownik A otwiera formularz dodawania wydatku w grupie.
2. Użytkownik A tworzy wydatek: „Pizza", 60 PLN, podział równy.
3. Zaobserwuj przeglądarkę Użytkownika B.

**Dane testowe:**
- Wydatek: `Pizza`
- Kwota: `60`
- Waluta: `PLN`
- Podział: `equal`

**Oczekiwany rezultat:** Na ekranie Użytkownika B pojawia się powiadomienie toast z informacją o nowym wydatku (np. „Nowy wydatek: Pizza - 60,00 PLN"). Lista wydatków Użytkownika B odświeża się automatycznie bez konieczności ręcznego przeładowania strony.

**Warunki końcowe:** Połączenie WebSocket pozostaje aktywne. Oba widoki (A i B) pokazują identyczną, aktualną listę wydatków grupy.

**Rzeczywisty rezultat:** Po utworzeniu wydatku „Pizza" przez Użytkownika A, backend wywołał `manager.broadcast_to_group()` z wiadomością typu `expense_created` zawierającą `expense_id`, `description` i `amount`. Klasa `ConnectionManager` iterowała po aktywnych połączeniach WebSocket grupy i wysłała JSON do przeglądarki Użytkownika B metodą `ws.send_json()`. Hook `useGroupWebSocket` na frontendzie Użytkownika B odebrał wiadomość, wyświetlił powiadomienie toast (react-hot-toast) z treścią „Nowy wydatek: Pizza - 60,00 PLN" oraz wywołał invalidację zapytań TanStack Query, co spowodowało automatyczne odświeżenie listy wydatków bez przeładowania strony. Połączenie WebSocket pozostało aktywne po wysłaniu wiadomości.

**Status:** Zaliczony

---

## TC-NEW-007: Zarządzanie członkami grupy - dodawanie i uprawnienia

**Opis:** Weryfikacja, czy administrator grupy może dodać nowego członka wyszukując go po adresie e-mail, a zwykły członek nie ma takiej możliwości.

**Warunki wstępne:**
- Istnieje grupa „Projekt zespołowy" z jednym adminem (Użytkownik A).
- Użytkownik C (`celina@test.pl`) jest zarejestrowany w systemie, ale nie należy do grupy.
- Użytkownik B jest zwykłym członkiem grupy.

**Kroki testowe:**
1. Zaloguj się jako Użytkownik A (admin).
2. Przejdź do zakładki „Members" w grupie.
3. Kliknij przycisk „Add Member".
4. Wyszukaj użytkownika po e-mailu: `celina@test.pl`.
5. Dodaj znalezionego użytkownika do grupy.
6. Wyloguj się i zaloguj jako Użytkownik B (zwykły członek).
7. Przejdź do zakładki „Members" w tej samej grupie.
8. Sprawdź, czy przycisk „Add Member" jest dostępny.

**Dane testowe:**
- E-mail nowego członka: `celina@test.pl`
- Rola admina: `Użytkownik A`
- Rola członka: `Użytkownik B`

**Oczekiwany rezultat:** Krok 5 - Użytkownik C pojawia się na liście członków z rolą „member". Krok 8 - Użytkownik B **nie widzi** przycisku „Add Member" lub przycisk jest nieaktywny - brak uprawnień do dodawania członków.

**Warunki końcowe:** Grupa posiada 3 członków: A (admin), B (member), C (member). Uprawnienia ról RBAC działają poprawnie.

**Rzeczywisty rezultat:** Użytkownik A (admin) wyszukał `celina@test.pl` przez endpoint `GET /auth/search?email=celina@test.pl` - system zwrócił dane użytkownika. Wywołanie `POST /groups/{group_id}/members/{user_id}` zakończyło się sukcesem (HTTP 200). Backend zweryfikował rolę admina (`membership.role == GroupRole.ADMIN`), sprawdził istnienie użytkownika docelowego oraz brak duplikatu członkostwa. Użytkownik C pojawił się na liście członków z rolą „member". Po zalogowaniu jako Użytkownik B (zwykły członek) i przejściu do zakładki „Members" - przycisk „Add Member" nie był widoczny. Próba bezpośredniego wywołania endpointu dodawania członka przez Użytkownika B zwróciła HTTP 403 z komunikatem „Only admins can add members". Mechanizm RBAC działa poprawnie na poziomie zarówno backendu, jak i frontendu.

**Status:** Zaliczony

---

## TC-NEW-008: Eksport historii wydatków grupy do pliku CSV *(planowana funkcjonalność)*

**Opis:** Weryfikacja funkcjonalności eksportu listy wydatków grupy do pliku CSV - potencjalna przyszła funkcja umożliwiająca archiwizację i analizę danych poza systemem.

**Warunki wstępne:**
- Użytkownik jest członkiem grupy „Wyjazd firmowy".
- Grupa posiada co najmniej 5 zarejestrowanych wydatków w różnych walutach i z różnymi typami podziału.

**Kroki testowe:**
1. Przejdź do listy wydatków grupy „Wyjazd firmowy".
2. Kliknij przycisk „Eksportuj do CSV" (lub analogiczny element UI).
3. Zapisz pobrany plik na dysku.
4. Otwórz plik w arkuszu kalkulacyjnym lub edytorze tekstu.
5. Porównaj zawartość pliku z danymi widocznymi w aplikacji.

**Dane testowe:**
- Grupa: `Wyjazd firmowy`
- Liczba wydatków: `≥ 5`
- Format eksportu: `CSV (UTF-8 z BOM)`

**Oczekiwany rezultat:** Plik CSV zostaje pobrany. Zawiera nagłówki kolumn: Data, Opis, Kwota, Waluta, Płatnik, Typ podziału, Uczestnicy. Wszystkie wydatki grupy są obecne w pliku. Polskie znaki diakrytyczne wyświetlają się poprawnie. Kwoty są sformatowane numerycznie (bez symboli walut).

**Warunki końcowe:** Plik CSV został zapisany na urządzeniu użytkownika. Dane w aplikacji pozostają nienaruszone - eksport jest operacją tylko do odczytu.

**Rzeczywisty rezultat:** Brak możliwości wykonania - funkcjonalność eksportu do CSV nie jest jeszcze zaimplementowana w aplikacji. W interfejsie brakuje przycisku „Eksportuj do CSV", a backend nie posiada odpowiedniego endpointu.

**Status:** Nie uruchomiono - funkcjonalność niezaimplementowana

---

## TC-NEW-009: Zaawansowane filtrowanie wydatków po zakresie dat i kwocie *(planowana funkcjonalność)*

**Opis:** Weryfikacja potencjalnej przyszłej funkcji zaawansowanego filtrowania - użytkownik powinien móc zawęzić listę wydatków grupy według zakresu dat oraz minimalnej/maksymalnej kwoty.

**Warunki wstępne:**
- Grupa „Rodzina" zawiera wydatki z różnych miesięcy:
  - Styczeń: 50 PLN, 200 PLN
  - Luty: 75 PLN, 500 PLN
  - Marzec: 30 PLN, 150 PLN
- Użytkownik jest zalogowany i ma otwartą listę wydatków grupy.

**Kroki testowe:**
1. Na liście wydatków grupy kliknij ikonę/przycisk „Filtruj".
2. Ustaw zakres dat: od **2026-02-01** do **2026-02-28**.
3. Ustaw zakres kwot: minimum **60 PLN**, maksimum **400 PLN**.
4. Zatwierdź filtry.
5. Sprawdź wyświetlone wyniki.
6. Kliknij przycisk „Wyczyść filtry".

**Dane testowe:**
- Zakres dat: `2026-02-01 – 2026-02-28`
- Kwota min: `60`
- Kwota max: `400`
- Oczekiwane wyniki: `1 wydatek (75 PLN z lutego)`

**Oczekiwany rezultat:** Po zastosowaniu filtrów wyświetla się wyłącznie 1 wydatek (75 PLN z lutego) - jedyny spełniający oba kryteria jednocześnie. Wydatek za 500 PLN z lutego jest odfiltrowany (przekracza max). Po wyczyszczeniu filtrów lista wraca do pełnego widoku z 6 wydatkami.

**Warunki końcowe:** Filtry nie modyfikują danych w bazie - działają wyłącznie na warstwie prezentacji. Po wyczyszczeniu filtrów stan listy jest identyczny jak przed filtrowaniem.

**Rzeczywisty rezultat:** Brak możliwości wykonania - funkcjonalność zaawansowanego filtrowania nie jest jeszcze zaimplementowana. Lista wydatków nie posiada opcji filtrowania po zakresie dat ani kwocie. Endpoint `GET /groups/{group_id}/expenses/` nie przyjmuje parametrów filtrujących.

**Status:** Nie uruchomiono - funkcjonalność niezaimplementowana

---

## TC-NEW-010: Generowanie raportu statystyk wydatków grupowych *(planowana funkcjonalność)*

**Opis:** Weryfikacja potencjalnej przyszłej funkcji generowania podsumowania statystycznego wydatków grupy - wykresy, ranking płatników, łączne wydatki na osobę w wybranym okresie.

**Warunki wstępne:**
- Grupa „Studenci" posiada co najmniej 10 wydatków zarejestrowanych w ciągu ostatnich 3 miesięcy.
- W grupie jest co najmniej 3 różnych płatników.

**Kroki testowe:**
1. Przejdź do strony grupy „Studenci".
2. Kliknij zakładkę lub przycisk „Statystyki / Raport".
3. Wybierz okres raportu: **ostatnie 3 miesiące**.
4. Przeanalizuj wygenerowane dane: wykres wydatków w czasie, podział na osoby, łączne kwoty.
5. Sprawdź, czy sumy na wykresie zgadzają się z danymi na liście wydatków.

**Dane testowe:**
- Grupa: `Studenci`
- Okres: `ostatnie 3 miesiące`
- Minimalna liczba wydatków: `10`
- Liczba płatników: `≥ 3`

**Oczekiwany rezultat:** System wyświetla czytelny raport zawierający: (1) wykres słupkowy/liniowy wydatków w czasie, (2) podsumowanie łącznych wydatków na osobę (ranking), (3) łączną kwotę wydatków grupy w wybranym okresie. Wszystkie wartości liczbowe są spójne z rzeczywistymi danymi. Raport obsługuje wydatki w różnych walutach - przelicza je na walutę główną.

**Warunki końcowe:** Raport został wygenerowany na podstawie danych tylko do odczytu. Żadne dane w bazie nie zostały zmodyfikowane.

**Rzeczywisty rezultat:** Brak możliwości wykonania - funkcjonalność raportów statystycznych nie jest jeszcze zaimplementowana. Strona grupy nie zawiera zakładki „Statystyki / Raport", a backend nie posiada endpointów agregujących dane wydatków w formie statystycznej.

**Status:** Nie uruchomiono - funkcjonalność niezaimplementowana
