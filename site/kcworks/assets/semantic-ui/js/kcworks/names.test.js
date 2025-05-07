import {
    getFullName,
    getFullNameInverted,
    getFamilyName,
    getGivenName,
} from "./names";

describe("Name utility functions", () => {
    describe("getFullName", () => {
        test.each([
            // Basic name
            [
                {
                    given: "John",
                    family: "Smith",
                },
                "John Smith",
            ],
            // Name with middle name
            [
                {
                    given: "John",
                    middle: "Robert",
                    family: "Smith",
                },
                "John Robert Smith",
            ],
            // Name with suffix
            [
                {
                    given: "John",
                    family: "Smith",
                    suffix: "Jr.",
                },
                "John Smith, Jr.",
            ],
            // Name with fixed prefix
            [
                {
                    given: "Jan",
                    family_prefix_fixed: "van",
                    family: "Helsing",
                },
                "Jan van Helsing",
            ],
            // Name with ibn prefix (as fixed prefix)
            [
                {
                    given: "Sina",
                    family_prefix_fixed: "ibn",
                    family: "Ali",
                },
                "Sina ibn Ali",
            ],
            // Complex name with all components
            [
                {
                    given: "John",
                    middle: "Robert",
                    family_prefix_fixed: "van",
                    family: "Helsing",
                    suffix: "III",
                },
                "John Robert van Helsing, III",
            ],
            // Name with nickname
            [
                {
                    given: "John",
                    nickname: "Jack",
                    family: "Smith",
                },
                "John Jack Smith",
            ],
            // Name with family prefix fixed (for O'Connor)
            [
                {
                    given: "John",
                    family_prefix_fixed: "O'",
                    family: "Connor",
                },
                "John O'Connor",
            ],
            // Name with spousal name
            [
                {
                    given: "Mary",
                    spousal: "Jones",
                    family: "Smith",
                },
                "Mary Jones Smith",
            ],
            // Chinese name (family name first)
            [
                {
                    family: "Li",
                    given: "Wei",
                    middle: "Ming",
                },
                "Wei Ming Li",
            ],
            // Japanese name (family name first)
            [
                {
                    family: "Tanaka",
                    given: "Hiroshi",
                    middle: "Yuki",
                },
                "Hiroshi Yuki Tanaka",
            ],
            // Russian name with patronymic
            [
                {
                    family: "Ivanov",
                    given: "Ivan",
                    parental: "Petrovich",
                },
                "Ivan Petrovich Ivanov",
            ],
        ])("should format name correctly: %p", (nameParts, expected) => {
            expect(getFullName(nameParts)).toBe(expected);
        });
    });

    describe("getFullNameInverted", () => {
        test.each([
            // Basic inverted name
            [
                {
                    given: "John",
                    family: "Smith",
                },
                "Smith, John",
            ],
            // Inverted name with middle name
            [
                {
                    given: "John",
                    middle: "Robert",
                    family: "Smith",
                },
                "Smith, John Robert",
            ],
            // Inverted name with suffix
            [
                {
                    given: "John",
                    family: "Smith",
                    suffix: "Jr.",
                },
                "Smith, John, Jr.",
            ],
            // Name with fixed prefix
            [
                {
                    given: "Jan",
                    family_prefix_fixed: "van",
                    family: "Helsing",
                },
                "van Helsing, Jan",
            ],
            // Name with ibn prefix (as fixed prefix)
            [
                {
                    given: "Sina",
                    family_prefix_fixed: "ibn",
                    family: "Ali",
                },
                "ibn Ali, Sina",
            ],
            // Complex name with fixed prefix
            [
                {
                    given: "Wolfgang",
                    middle: "Amadeus",
                    family_prefix: "von",
                    family: "Mozart",
                    suffix: "Jr.",
                },
                "Mozart, Wolfgang Amadeus von, Jr.",
            ],
            // Complex name with ibn prefix (as fixed prefix)
            [
                {
                    given: "Rushd",
                    middle: "Averroes",
                    family_prefix_fixed: "ibn",
                    family: "Ahmad",
                    suffix: "al-Andalusi",
                },
                "ibn Ahmad, Rushd Averroes, al-Andalusi",
            ],
            // Name with family prefix fixed (for O'Connor)
            [
                {
                    given: "John",
                    family_prefix_fixed: "O'",
                    family: "Connor",
                },
                "O'Connor, John",
            ],
            // Chinese name inverted
            [
                {
                    family: "Li",
                    given: "Wei",
                    middle: "Ming",
                },
                "Li, Wei Ming",
            ],
            // Japanese name inverted
            [
                {
                    family: "Tanaka",
                    given: "Hiroshi",
                    middle: "Yuki",
                },
                "Tanaka, Hiroshi Yuki",
            ],
            // Russian name with patronymic inverted
            [
                {
                    family: "Ivanov",
                    given: "Ivan",
                    parental: "Petrovich",
                },
                "Ivanov, Ivan Petrovich",
            ],
        ])("should format inverted name correctly: %p", (nameParts, expected) => {
            expect(getFullNameInverted(nameParts)).toBe(expected);
        });
    });

    describe("getFamilyName", () => {
        test.each([
            // Basic family name
            [
                {
                    family: "Smith",
                },
                "Smith",
            ],
            // Family name with fixed prefix
            [
                {
                    family_prefix_fixed: "van",
                    family: "Helsing",
                },
                "van Helsing",
            ],
            // Family name with fixed prefix
            [
                {
                    family_prefix_fixed: "de la",
                    family: "Cruz",
                },
                "de la Cruz",
            ],
            // Family name with O'Connor prefix
            [
                {
                    family_prefix_fixed: "O'",
                    family: "Connor",
                },
                "O'Connor",
            ],
            // Family name with spousal name
            [
                {
                    spousal: "Jones",
                    family: "Smith",
                },
                "Jones Smith",
            ],
            // Complex family name
            [
                {
                    family_prefix_fixed: "de",
                    spousal: "Jones",
                    family: "Smith",
                    last: "III",
                },
                "de Jones Smith III",
            ],
            // Chinese family name
            [
                {
                    family: "Li",
                },
                "Li",
            ],
            // Japanese family name
            [
                {
                    family: "Tanaka",
                },
                "Tanaka",
            ],
            // Russian family name
            [
                {
                    family: "Ivanov",
                },
                "Ivanov",
            ],
        ])("should format family name correctly: %p", (nameParts, expected) => {
            expect(getFamilyName(nameParts)).toBe(expected);
        });
    });

    describe("getGivenName", () => {
        test.each([
            // Basic given name
            [
                {
                    given: "John",
                },
                "John",
            ],
            // Given name with middle name
            [
                {
                    given: "John",
                    middle: "Robert",
                },
                "John Robert",
            ],
            // Given name with nickname
            [
                {
                    given: "John",
                    nickname: "Jack",
                },
                "John Jack",
            ],
            // Given name with first and middle
            [
                {
                    first: "John",
                    middle: "Robert",
                },
                "John Robert",
            ],
            // Complex given name
            [
                {
                    first: "Johnny",
                    given: "John",
                    middle: "Robert",
                    nickname: "Jack",
                },
                "Johnny John Robert Jack",
            ],
            // Chinese given name
            [
                {
                    given: "Wei",
                    middle: "Ming",
                },
                "Wei Ming",
            ],
            // Japanese given name
            [
                {
                    given: "Hiroshi",
                    middle: "Yuki",
                },
                "Hiroshi Yuki",
            ],
            // Russian given name with patronymic
            [
                {
                    given: "Ivan",
                    parental: "Petrovich",
                },
                "Ivan Petrovich",
            ],
        ])("should format given name correctly: %p", (nameParts, expected) => {
            expect(getGivenName(nameParts)).toBe(expected);
        });
    });

    describe("Edge cases", () => {
        test("should handle null or undefined name parts", () => {
            expect(getFullName(null)).toBe("");
            expect(getFullNameInverted(null)).toBe("");
            expect(getFamilyName(null)).toBe("");
            expect(getGivenName(null)).toBe("");
        });

        test("should handle empty name parts", () => {
            expect(getFullName({})).toBe("");
            expect(getFullNameInverted({})).toBe("");
            expect(getFamilyName({})).toBe("");
            expect(getGivenName({})).toBe("");
        });

        test("should handle missing optional fields", () => {
            expect(getFullName({ family: "Smith" })).toBe("Smith");
            expect(getFullNameInverted({ family: "Smith" })).toBe("Smith");
            expect(getFamilyName({ family: "Smith" })).toBe("Smith");
            expect(getGivenName({ family: "Smith" })).toBe("");
        });
    });
});