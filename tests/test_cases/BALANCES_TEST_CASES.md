# Przypadki Testowe: Zakładka Salda (Balances)

## TC-BAL-001: Wyświetlanie całkowitego salda (Total Balance)
**Opis:** Weryfikacja, czy całkowite saldo jest poprawnie obliczane i wyświetlane na górze zakładki.
**Warunki wstępne:** Użytkownik posiada co najmniej jedno aktywne konto z dodatnim saldem.
**Kroki:**
1. Zaloguj się do aplikacji.
2. Przejdź do zakładki "Balances".
**Oczekiwany rezultat:** Całkowite saldo (suma z wszystkich podpiętych kont) jest poprawnie wyświetlane wraz z odpowiednim symbolem waluty.

## TC-BAL-002: Wyświetlanie sald dla poszczególnych kont
**Opis:** Sprawdzenie, czy lista kont (np. Gotówka, Karta debetowa, Oszczędności) jest widoczna wraz z ich indywidualnymi saldami.
**Warunki wstępne:** Użytkownik ma dodane co najmniej dwa różne konta z przypisanymi środkami.
**Kroki:**
1. Przejdź do zakładki "Balances".
**Oczekiwany rezultat:** Wszystkie konta użytkownika są wylistowane, a obok każdego z nich widnieje jego aktualny, poprawny stan konta. Suma sald kont odpowiada całkowitemu saldu.

## TC-BAL-003: Aktualizacja salda po dodaniu nowego wydatku
**Opis:** Weryfikacja, czy saldo zmniejsza się natychmiast po zarejestrowaniu nowej transakcji wychodzącej.
**Warunki wstępne:** Użytkownik znajduje się w zakładce "Balances", znane jest obecne saldo konta X.
**Kroki:**
1. Zapisz obecne saldo całkowite oraz saldo konta X.
2. Przejdź do dodawania transakcji i dodaj wydatek na kwotę 50 PLN z konta X.
3. Wróć do zakładki "Balances".
**Oczekiwany rezultat:** Saldo konta X oraz saldo całkowite zostały pomniejszone dokładnie o 50 PLN.

## TC-BAL-004: Aktualizacja salda po dodaniu nowego przychodu
**Opis:** Weryfikacja, czy saldo zwiększa się poprawnie po dodaniu transakcji przychodowej (np. wypłata).
**Warunki wstępne:** Użytkownik znajduje się w zakładce "Balances", znane jest obecne saldo konta Y.
**Kroki:**
1. Zapisz obecne saldo całkowite oraz saldo konta Y.
2. Dodaj przychód na kwotę 2000 PLN na konto Y.
3. Wróć do zakładki "Balances".
**Oczekiwany rezultat:** Saldo konta Y oraz saldo całkowite zostały powiększone dokładnie o 2000 PLN.

## TC-BAL-005: Wyświetlanie pustego stanu
**Opis:** Sprawdzenie zachowania zakładki w sytuacji, gdy użytkownik nie założył jeszcze żadnego konta i nie ma historii transakcji.
**Warunki wstępne:** Nowo zarejestrowane konto użytkownika bez żadnych danych.
**Kroki:**
1. Zaloguj się na nowe konto.
2. Przejdź do zakładki "Balances".
**Oczekiwany rezultat:** Wyświetla się przyjazny komunikat o braku kont ("Empty state") wraz z widocznym przyciskiem CTA (Call to Action) zachęcającym do "Dodania pierwszego konta". Saldo całkowite wynosi 0.00.

## TC-BAL-006: Formatowanie waluty i poprawne zaokrąglanie
**Opis:** Weryfikacja, czy kwoty są poprawnie sformatowane, posiadają separator tysięcy i zawsze wyświetlają dwa miejsca po przecinku.
**Warunki wstępne:** Konto posiada saldo równe 1234567.893 PLN.
**Kroki:**
1. Przejdź do zakładki "Balances".
**Oczekiwany rezultat:** Saldo wyświetla się sformatowane jako `1 234 567,89 PLN` (lub zgodnie z ustawieniami regionalnymi, np. `1,234,567.89 PLN`), po prawidłowym zaokrągleniu z 3 miejsc po przecinku.

## TC-BAL-007: Obsługa i wyświetlanie salda ujemnego
**Opis:** Weryfikacja wizualnej i logicznej obsługi ujemnego salda (np. w przypadku kart kredytowych lub debetu).
**Warunki wstępne:** Użytkownik dodaje wydatek przewyższający obecne saldo na danym koncie.
**Kroki:**
1. Dla konta z saldem 100 PLN dodaj wydatek w wysokości 150 PLN.
2. Przejdź do zakładki "Balances".
**Oczekiwany rezultat:** Saldo tego konta wynosi `-50.00 PLN`. Wartość ujemna jest wyraźnie oznaczona (np. na czerwono lub ze znakiem minusa), a saldo całkowite zostało o tę kwotę odpowiednio zredukowane.

## TC-BAL-008: Przeliczanie salda w wielu walutach
**Opis:** Sprawdzenie, czy aplikacja poprawnie konwertuje i sumuje salda z kont prowadzonych w różnych walutach na główną walutę profilu.
**Warunki wstępne:** Główna waluta aplikacji to PLN. Użytkownik posiada konto "Gotówka" (100 PLN) i konto "Euro" (100 EUR). Zdefiniowany kurs wymiany to np. 1 EUR = 4.30 PLN.
**Kroki:**
1. Przejdź do zakładki "Balances".
**Oczekiwany rezultat:** Konto Euro wyświetla saldo `100.00 EUR`. Saldo całkowite na samej górze wynosi `530.00 PLN` (100 zł + 430 zł po przeliczeniu).

## TC-BAL-009: Ukrywanie i odkrywanie salda (Tryb prywatności)
**Opis:** Weryfikacja działania przycisku (np. ikony "oka") służącego do ukrywania wrażliwych danych o stanie konta przed osobami postronnymi.
**Warunki wstępne:** Widoczne są salda kont.
**Kroki:**
1. Kliknij ikonę ukrywania salda (ikona oka).
2. Odśwież widok/przejdź do innej zakładki i wróć.
3. Kliknij ikonę ponownie.
**Oczekiwany rezultat:** Po pierwszym kliknięciu wszystkie kwoty sald zamieniają się w maskę (np. `*** PLN`). Stan ukrycia zostaje zapamiętany po odświeżeniu. Po ponownym kliknięciu dokładne kwoty są znowu widoczne.

## TC-BAL-010: Usuwanie konta (Account Deletion)
**Opis:** Weryfikacja, czy użytkownik może bezpowrotnie usunąć swoje konto z systemu, a powiązane z nim transakcje zostaną wyczyszczone.
**Warunki wstępne:** Użytkownik posiada co najmniej jedno konto (np. z saldem 150 PLN).
**Kroki:**
1. Przejdź do zakładki "Balances".
2. Na karcie wybranego konta kliknij przycisk "Delete" u dołu ekranu.
3. W oknie dialogowym przeglądarki (alert) potwierdź chęć usunięcia konta klikając "OK".
**Oczekiwany rezultat:** Konto trwale znika z listy "Your Accounts". Saldo całkowite w polu "Total Balance" zostaje automatycznie pomniejszone o wartość salda usuniętego konta.

