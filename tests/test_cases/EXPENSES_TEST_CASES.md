```
Wojciech Domański PS6
```
Przypadki testowe dla funkcjonalności dodawania wydatków

TC_001

Opis: Dodanie wydatku z równym podziałem (equal).
Warunki wstępne: Użytkownik jest zalogowany, członkiem grupy, modal dodawania wydatku jest
otwarty.

Kroki testowe:

1. Wprowadź opis ("Obiad").
2. Wprowadź kwotę (100.00).
3. Wybierz walutę (PLN).
4. Wybierz typ podziału "equal".
5. Wybierz datę (dzisiejszą).
6. Wybierz wszystkich uczestników (user1, user2).
7. Kliknij przycisk "Add Expense".

Dane testowe: Opis: Obiad, Kwota: 100.00, Waluta: PLN, Typ podziału: equal, Data: 2026- 03 - 14,
Uczestnicy: user1, user2.

Oczekiwany rezultat: Wydatek zostaje dodany, wyświetla się komunikat sukcesu, modal się
zamyka, wydatek pojawia się na liście wydatków grupy, każdy uczestnik ma dług 50.00 PLN.

TC_002

Opis: Dodanie wydatku z podziałem kwotowym (exact).
Warunki wstępne: Użytkownik jest zalogowany i członkiem grupy, modal dodawania wydatku jest
otwarty.

Kroki testowe:

1. Wprowadź opis ("Obiad").
2. Wprowadź kwotę (150.00).
3. Wybierz walutę (PLN).
4. Wybierz typ podziału "exact".
5. Wybierz datę (dzisiejszą).
6. Wybierz uczestników (user1, user2).
7. Wprowadź dokładne kwoty dla każdego uczestnika (user1: 50.00, user2: 100.00).
8. Kliknij przycisk "Add Expense".

Dane testowe: Opis: Obiad, Kwota: 150.00, Waluta: PLN, Typ podziału: exact, Data: 2026- 03 - 14,
Uczestnicy: user1, user2, Kwoty: user1=50.00, user2=100.00.


Oczekiwany rezultat: Wydatek zostaje dodany, wyświetla się komunikat sukcesu, modal się
zamyka, wydatek pojawia się na liście, długi odpowiadają wprowadzonym kwotom.

TC_003

Opis: Dodanie wydatku z podziałem procentowym (percent).
Warunki wstępne: Użytkownik jest zalogowany i członkiem grupy, modal dodawania wydatku jest
otwarty.

Kroki testowe:

1. Wprowadź opis ("Obiad").
2. Wprowadź kwotę (200.00).
3. Wybierz walutę (PLN).
4. Wybierz typ podziału "percent".
5. Wybierz datę (dzisiejszą).
6. Wybierz uczestników (user1, user2).
7. Wprowadź procenty dla każdego uczestnika (user1: 30, user2: 70).
8. Kliknij przycisk "Add Expense".

Dane testowe: Opis: Obiad, Kwota: 200.00, Waluta: PLN, Typ podziału: percent, Data: 2026- 03 -
14, Uczestnicy: user1, user2, Procenty: user1=30, user2=70.

Oczekiwany rezultat: Wydatek zostaje dodany, wyświetla się komunikat sukcesu, modal się
zamyka, wydatek pojawia się na liście, długi odpowiadają procentom (user1: 60.00, user2:
140.00).

TC_004

Opis: Dodanie wydatku z podziałem udziałowym (shares).
Warunki wstępne: Użytkownik jest zalogowany i członkiem grupy, modal dodawania wydatku jest
otwarty.

Kroki testowe:

1. Wprowadź opis ("Obiad").
2. Wprowadź kwotę (120.00).
3. Wybierz walutę (PLN).
4. Wybierz typ podziału "shares".
5. Wybierz datę (dzisiejszą).
6. Wybierz uczestników (user1, user2, user3).
7. Wprowadź udziały dla każdego uczestnika (user1: 1, user2: 2, user3: 1).
8. Kliknij przycisk "Add Expense".


Dane testowe: Opis: Obiad, Kwota: 120.00, Waluta: PLN, Typ podziału: shares, Data: 2026- 03 -
14, Uczestnicy: user1, user2, user3, Udziały: user1=1, user2=2, user3=1.

Oczekiwany rezultat: Wydatek zostaje dodany, wyświetla się komunikat sukcesu, modal się
zamyka, wydatek pojawia się na liście, długi odpowiadają udziałom (user1: 30.00, user2: 60.00,
user3: 30.00).

TC_005

Opis: Dodanie wydatku z ujemną kwotą.
Warunki wstępne: Użytkownik jest zalogowany i członkiem grupy, modal dodawania wydatku jest
otwarty.

Kroki testowe:

1. Wprowadź opis ("Obiad").
2. Wprowadź kwotę (-50.00).
3. Wybierz walutę (PLN).
4. Wybierz typ podziału "equal".
5. Wybierz datę (dzisiejszą).
6. Wybierz uczestników (user1, user2).
7. Kliknij przycisk "Add Expense".

Dane testowe: Opis: Obiad, Kwota: -50.00, Waluta: PLN, Typ podziału: equal, Data: 2026- 03 - 14,
Uczestnicy: user1, user2.

Oczekiwany rezultat: Dodanie kończy się niepowodzeniem, wyświetla się komunikat błędu
("Wartość nie może być mniejsza niż 0, 01 ."), modal pozostaje otwarty.

TC_006

Opis: Dodanie wydatku bez wybranych uczestników.
Warunki wstępne: Użytkownik jest zalogowany i członkiem grupy, modal dodawania wydatku jest
otwarty.

Kroki testowe:

1. Wprowadź opis ("Obiad").
2. Wprowadź kwotę (100.00).
3. Wybierz walutę (PLN).
4. Wybierz typ podziału "equal".
5. Wybierz datę (dzisiejszą).
6. Nie zaznaczaj żadnych uczestników.
7. Kliknij przycisk "Add Expense".

Dane testowe: Opis: Obiad, Kwota: 100.00, Waluta: PLN, Typ podziału: equal, Data: 2026- 03 - 14,
Uczestnicy: (brak).


Oczekiwany rezultat: Dodanie kończy się niepowodzeniem, wyświetla się komunikat błędu
("Przynajmniej jeden użytkownik powinien być wybrany."), modal pozostaje otwarty.

TC_007

Opis: Dodanie wydatku z datą w przyszłości.
Warunki wstępne: Użytkownik jest zalogowany i członkiem grupy, modal dodawania wydatku jest
otwarty.

Kroki testowe:

1. Wprowadź opis ("Przyszły wydatek").
2. Wprowadź kwotę (75.00).
3. Wybierz walutę (PLN).
4. Wybierz typ podziału "equal".
5. Wybierz datę w przyszłości ( 2026 - 04 - 01).
6. Wybierz uczestników (user1, user2).
7. Kliknij przycisk "Add Expense".

Dane testowe: Opis: Przyszły wydatek, Kwota: 75.00, Waluta: PLN, Typ podziału: equal, Data:
2026 - 04 - 01, Uczestnicy: user1, user2.

Oczekiwany rezultat: Wydatek zostaje dodany, wyświetla się komunikat sukcesu, modal się
zamyka, wydatek pojawia się na liście z przyszłą datą.

TC_008

Opis: Dodanie wydatku z pustym opisem.
Warunki wstępne: Użytkownik jest zalogowany i członkiem grupy, modal dodawania wydatku jest
otwarty.

Kroki testowe:

1. Pozostaw opis pusty.
2. Wprowadź kwotę (50.00).
3. Wybierz walutę (PLN).
4. Wybierz typ podziału "equal".
5. Wybierz datę (dzisiejszą).
6. Wybierz uczestników (user1).
7. Kliknij przycisk "Add Expense".

Dane testowe: Opis: (pusty), Kwota: 50.00, Waluta: PLN, Typ podziału: equal, Data: 2026- 03 - 14,
Uczestnicy: user1.

Oczekiwany rezultat: Dodanie kończy się niepowodzeniem, przeglądarka wyświetla komunikat
walidacji ("Wypełnij te pole."), modal pozostaje otwarty.


## TC_009

Opis: Dodanie wydatku z niekompletnymi danymi dla podziału exact (brakujące kwoty).
Warunki wstępne: Użytkownik jest zalogowany i członkiem grupy, modal dodawania wydatku jest
otwarty.

Kroki testowe:

1. Wprowadź opis ("Obiad").
2. Wprowadź kwotę (100.00).
3. Wybierz walutę (PLN).
4. Wybierz typ podziału "exact".
5. Wybierz datę (dzisiejszą).
6. Wybierz uczestników (user1, user2).
7. Wprowadź kwotę tylko dla jednego uczestnika (user1: 50.00, user2: brak).
8. Kliknij przycisk "Add Expense".

Dane testowe: Opis: Obiad, Kwota: 100.00, Waluta: PLN, Typ podziału: exact, Data: 2026- 03 - 14,
Uczestnicy: user1, user2, Kwoty: user1=50.00, user2=(brak).

Oczekiwany rezultat: Dodanie kończy się niepowodzeniem, wyświetla się komunikat błędu
("Exact amounts sum to 50, but total is 100"), modal pozostaje otwarty.

TC_010

Opis: Dodanie wydatku przez członka grupy (sprawdzenie uprawnień).
Warunki wstępne: Użytkownik jest zalogowany i członkiem grupy (rola member), modal
dodawania wydatku jest otwarty.

Kroki testowe:

1. Wprowadź opis ("Obiad").
2. Wprowadź kwotę (80.00).
3. Wybierz walutę (PLN).
4. Wybierz typ podziału "equal".
5. Wybierz datę (dzisiejszą).
6. Wybierz uczestników (user1, user2).
7. Kliknij przycisk "Add Expense".

Dane testowe: Opis: Obiad, Kwota: 80.00, Waluta: PLN, Typ podziału: equal, Data: 2026- 03 - 14,
Uczestnicy: user1, user2.

Oczekiwany rezultat: Wydatek zostaje dodany, wyświetla się komunikat sukcesu, modal się
zamyka, wydatek pojawia się na liście (każdy członek może dodawać wydatki)


