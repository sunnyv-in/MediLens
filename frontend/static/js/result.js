
document.addEventListener("DOMContentLoaded", () => {

    console.log("MediLens result.js loaded");

    // ============================================
    // 1. CONFIGURATION
    // ============================================

    const configElement = document.getElementById("resultConfig");

    if (!configElement) {
        console.error("MediLens: resultConfig was not found.");
        return;
    }

    let config;

    try {
        config = JSON.parse(configElement.textContent);
    } catch (error) {
        console.error("MediLens: Invalid result configuration.", error);
        return;
    }

    const originalExplanation = String(
        config.originalExplanation || ""
    );

    const translationUrl = config.translationUrl;


    // ============================================
    // 2. HTML ELEMENTS
    // ============================================

    const languageSelect =
        document.getElementById("translateLangSelect");

    const explanation =
        document.getElementById("aiExplanationText");

    const status =
        document.getElementById("translationStatus");

    const speakBtn =
        document.getElementById("speakBtn");

    const pauseBtn =
        document.getElementById("pauseBtn");

    const stopBtn =
        document.getElementById("stopBtn");

    const speakLabel =
        document.getElementById("speakBtnLabel");

    const pauseLabel =
        document.getElementById("pauseBtnLabel");


    if (
        !languageSelect ||
        !explanation ||
        !status ||
        !speakBtn ||
        !pauseBtn ||
        !stopBtn ||
        !speakLabel ||
        !pauseLabel
    ) {
        console.error("MediLens: One or more result-page controls are missing.");
        return;
    }


    // ============================================
    // 3. APPLICATION STATE
    // ============================================

    let currentText = originalExplanation;

    let currentLanguage = "en";

    let speechChunks = [];

    let speechIndex = 0;

    let speechToken = 0;

    let translationToken = 0;

    let currentUtterance = null;

    const languageLocales = {

        en: "en-IN",
        hi: "hi-IN",
        mr: "mr-IN",
        ta: "ta-IN",
        te: "te-IN",
        bn: "bn-IN",
        gu: "gu-IN",
        kn: "kn-IN",
        ml: "ml-IN",
        pa: "pa-IN"

    };


    // ============================================
    // 4. SAFE MARKDOWN TEXT RENDERER
    // ============================================

    /*
       Supports:
       **bold text**
       *italic text*
       __bold text__
       _italic text_
       `inline code`

       Creates actual HTML elements instead of injecting
       untrusted AI-generated HTML into the page.
    */

    function appendFormattedText(parent, text) {

        const pattern =
            /\*\*([^*]+?)\*\*|__([^_]+?)__|\*([^*]+?)\*|_([^_]+?)_|`([^`]+?)`/g;

        let lastIndex = 0;

        let match;

        while ((match = pattern.exec(text)) !== null) {

            // Insert normal text before the formatted section.

            parent.appendChild(
                document.createTextNode(
                    text.slice(lastIndex, match.index)
                )
            );

            let element;

            let content;

            if (match[1] !== undefined) {

                element = document.createElement("strong");
                content = match[1];

            } else if (match[2] !== undefined) {

                element = document.createElement("strong");
                content = match[2];

            } else if (match[3] !== undefined) {

                element = document.createElement("em");
                content = match[3];

            } else if (match[4] !== undefined) {

                element = document.createElement("em");
                content = match[4];

            } else {

                element = document.createElement("code");
                content = match[5];

            }

            element.textContent = content;

            parent.appendChild(element);

            lastIndex = pattern.lastIndex;

        }


        // Remaining normal text.

        parent.appendChild(
            document.createTextNode(
                text.slice(lastIndex)
            )
        );

    }


    // ============================================
    // 5. RENDER COMPLETE EXPLANATION
    // ============================================

    function renderExplanation(text) {

        explanation.replaceChildren();

        const cleanInput = String(text || "")
            .replace(/\r\n?/g, "\n")
            .trim();

        if (!cleanInput) {

            const emptyMessage = document.createElement("p");

            emptyMessage.textContent =
                "No medicine explanation is available.";

            explanation.appendChild(emptyMessage);

            return;

        }


        // Separate natural paragraphs.

        const paragraphs = cleanInput
            .split(/\n\s*\n/)
            .map(item => item.trim())
            .filter(Boolean);


        paragraphs.forEach(rawParagraph => {

            const paragraph = document.createElement("p");

            // Convert single line breaks inside a paragraph
            // into spaces without removing paragraph structure.

            const content = rawParagraph
                .replace(/\s*\n\s*/g, " ")
                .trim();

            appendFormattedText(paragraph, content);

            explanation.appendChild(paragraph);

        });

    }


    // Render original explanation immediately.

    renderExplanation(originalExplanation);


    // ============================================
    // 6. TRANSLATION LANGUAGE CONFIGURATION
    // ============================================

    languageSelect.addEventListener(
        "change",
        translateExplanation
    );


    // ============================================
    // 7. TRANSLATE EXPLANATION
    // ============================================

    async function translateExplanation() {

        // Stop narration when changing language.

        stopSpeech();

        const targetLanguage = languageSelect.value;

        const requestId = ++translationToken;


        // Restore original English explanation.

        if (targetLanguage === "en") {

            currentText = originalExplanation;

            currentLanguage = "en";

            renderExplanation(originalExplanation);

            status.hidden = true;

            return;

        }


        if (!translationUrl) {

            status.hidden = false;

            status.textContent =
                "Translation service URL is missing.";

            console.error("MediLens: Translation URL missing.");

            languageSelect.value = currentLanguage;

            return;

        }


        status.hidden = false;

        status.textContent =
            "Translating your medicine explanation...";

        languageSelect.disabled = true;


        try {

            console.log(
                "MediLens: Translation requested for",
                targetLanguage
            );


            const response = await fetch(translationUrl, {

                method: "POST",

                headers: {

                    "Content-Type": "application/json",

                    "Accept": "application/json"

                },

                body: JSON.stringify({

                    text: originalExplanation,

                    target_lang: targetLanguage

                })

            });


            const data = await response.json();


            if (!response.ok) {

                throw new Error(
                    data.error || "Translation request failed."
                );

            }


            // Ignore old responses when a newer request exists.

            if (requestId !== translationToken) {
                return;
            }


            if (!data.success || !data.translated_text) {

                throw new Error(
                    data.error || "No translated explanation received."
                );

            }


            // Save translated text.

            currentText = String(data.translated_text);

            currentLanguage = targetLanguage;


            // Render translated paragraphs and emphasis.

            renderExplanation(currentText);


            status.hidden = true;


            console.log(
                "MediLens: Translation successful.",
                targetLanguage
            );


        } catch (error) {

            if (requestId !== translationToken) {
                return;
            }

            console.error(
                "MediLens translation error:",
                error
            );


            status.textContent =
                "Translation failed. Please try again.";

            status.hidden = false;


            // Keep the currently displayed language consistent.

            languageSelect.value = currentLanguage;


        } finally {

            if (requestId === translationToken) {

                languageSelect.disabled = false;

            }

        }

    }


    // ============================================
    // 8. CLEAN TEXT FOR NARRATION
    // ============================================

    /*
       Important:
       Narration reads only the explanation area.

       It does not read:
       - HTML tags
       - Bold or italic markers
       - Markdown headings
       - Markdown list symbols
       - Backticks
       - Link URLs
       - Formatting characters

       The browser reads the actual words displayed on screen.
    */

    function getNarrationText() {

        // Read the rendered explanation, not the raw AI response.

        let text =
            explanation.innerText ||
            explanation.textContent ||
            currentText;


        // Remove Markdown links but retain their visible labels.

        text = text.replace(
            /!?\[([^\]]*)\]\([^)]+\)/g,
            "$1"
        );


        // Remove Markdown formatting.

        text = text

            // Bold and italic.
            .replace(/\*\*/g, "")
            .replace(/\*/g, "")

            .replace(/__/g, "")
            .replace(/_/g, "")

            // Inline code.
            .replace(/`/g, "")

            // Markdown headings.
            .replace(/^#{1,6}\s*/gm, "")

            // Markdown blockquotes.
            .replace(/^\s*>\s?/gm, "")

            // Bullet characters and numbered list prefixes.
            .replace(/^\s*(?:[-+•]|\d+[.)])\s+/gm, "")

            // Markdown strikethrough.
            .replace(/~~/g, "")

            // Horizontal rules.
            .replace(/^\s*[-*_]{3,}\s*$/gm, "");


        // Remove invisible Unicode formatting characters.

        text = text.replace(
            /[\u200B-\u200D\uFEFF]/g,
            ""
        );


        // Normalize whitespace while retaining natural punctuation.

        text = text
            .replace(/\s+/g, " ")
            .trim();


        return text;

    }


    // ============================================
    // 9. LOAD AVAILABLE SPEECH VOICES
    // ============================================

    function getAvailableVoices() {

        if (!("speechSynthesis" in window)) {

            return Promise.resolve([]);

        }


        const initialVoices =
            window.speechSynthesis.getVoices();


        if (initialVoices.length > 0) {

            return Promise.resolve(initialVoices);

        }


        return new Promise(resolve => {

            let completed = false;


            function finish() {

                if (completed) return;

                completed = true;

                window.speechSynthesis.removeEventListener(
                    "voiceschanged",
                    finish
                );

                resolve(
                    window.speechSynthesis.getVoices()
                );

            }


            window.speechSynthesis.addEventListener(
                "voiceschanged",
                finish
            );


            // Do not wait forever if the browser does not
            // fire the voiceschanged event.

            setTimeout(finish, 2500);

        });

    }


    // ============================================
    // 10. FIND THE CORRECT LANGUAGE VOICE
    // ============================================

    function findVoice(voices, language) {

        const targetLocale =
            languageLocales[language] || language;


        if (!voices || !voices.length) {
            return null;
        }


        // Prefer exact locale match.

        let selectedVoice = voices.find(voice =>

            voice.lang.toLowerCase() ===
            targetLocale.toLowerCase()

        );


        if (selectedVoice) {
            return selectedVoice;
        }


        // Accept regional variations of the language.

        selectedVoice = voices.find(voice =>

            voice.lang.toLowerCase().startsWith(
                language.toLowerCase() + "-"
            )

        );


        if (selectedVoice) {
            return selectedVoice;
        }


        // English can use another installed English voice.

        if (language === "en") {

            return voices.find(voice =>
                voice.lang.toLowerCase().startsWith("en")
            ) || null;

        }


        // Never silently use an English voice for Hindi.

        return null;

    }


    // ============================================
    // 11. SPLIT TEXT INTO NATURAL SPEECH CHUNKS
    // ============================================

    function splitText(text, maxLength = 180) {

        const cleanText = String(text || "").trim();

        if (!cleanText) {
            return [];
        }


        // Split on sentence-ending punctuation followed by
        // whitespace. Decimal values such as 1.25 are preserved.

        const sentences = cleanText
            .split(/(?<=[.!?।])\s+/u)
            .map(sentence => sentence.trim())
            .filter(Boolean);


        const chunks = [];

        let current = "";


        sentences.forEach(sentence => {

            // Break extremely long sentences at word boundaries.

            if (sentence.length > maxLength) {

                if (current) {

                    chunks.push(current.trim());

                    current = "";

                }


                const words = sentence.split(/\s+/);

                let segment = "";


                words.forEach(word => {

                    if (
                        (segment + " " + word).trim().length >
                        maxLength &&
                        segment
                    ) {

                        chunks.push(segment.trim());

                        segment = word;

                    } else {

                        segment = segment
                            ? segment + " " + word
                            : word;

                    }

                });


                if (segment.trim()) {

                    current = segment.trim();

                }

                return;

            }


            // Keep normal sentences together where possible.

            const candidate = current
                ? current + " " + sentence
                : sentence;


            if (
                candidate.length > maxLength &&
                current
            ) {

                chunks.push(current.trim());

                current = sentence;

            } else {

                current = candidate;

            }

        });


        if (current.trim()) {

            chunks.push(current.trim());

        }


        return chunks;

    }


    // ============================================
    // 12. SPEECH BUTTON
    // ============================================

    speakBtn.addEventListener(
        "click",
        startSpeech
    );


    // ============================================
    // 13. START NARRATION
    // ============================================

    async function startSpeech() {

        if (!("speechSynthesis" in window)) {

            alert(
                "Your browser does not support text-to-speech."
            );

            return;

        }


        // Get clean text from the actual visible explanation.

        const narrationText = getNarrationText();


        if (!narrationText) {

            alert(
                "No explanation is available for narration."
            );

            return;

        }


        // Stop any existing speech.

        stopSpeech();


        const token = ++speechToken;


        speakLabel.textContent = "Loading...";


        try {

            const voices = await getAvailableVoices();


            // Ignore outdated speech requests.

            if (token !== speechToken) {
                return;
            }


            const voice = findVoice(
                voices,
                currentLanguage
            );


            if (!voice) {

                resetSpeechControls();

                alert(
                    `No ${languageLocales[currentLanguage] || currentLanguage} ` +
                    "speech voice is installed on this device. " +
                    "Please check your operating system's language settings."
                );

                return;

            }


            // Clean and divide only the displayed text.

            speechChunks = splitText(narrationText);

            speechIndex = 0;


            if (!speechChunks.length) {

                resetSpeechControls();

                return;

            }


            speakLabel.textContent = "Playing...";

            pauseBtn.hidden = false;

            stopBtn.hidden = false;


            console.log(
                "MediLens narration started.",
                {
                    language: currentLanguage,
                    voice: voice.name,
                    locale: voice.lang,
                    chunks: speechChunks.length,
                    textLength: narrationText.length
                }
            );


            speakNext(token, voice);


        } catch (error) {

            console.error(
                "MediLens speech initialization error:",
                error
            );

            stopSpeech();

        }

    }


    // ============================================
    // 14. SPEAK NEXT CHUNK
    // ============================================

    function speakNext(token, voice) {

        if (token !== speechToken) {
            return;
        }


        if (speechIndex >= speechChunks.length) {

            resetSpeechControls();

            currentUtterance = null;

            console.log("MediLens narration completed.");

            return;

        }


        const chunk = speechChunks[speechIndex];


        const utterance =
            new SpeechSynthesisUtterance(chunk);


        utterance.voice = voice;

        utterance.lang = voice.lang;

        utterance.rate = 0.92;

        utterance.pitch = 1;

        utterance.volume = 1;


        currentUtterance = utterance;


        utterance.onstart = () => {

            if (token !== speechToken) return;

            speakLabel.textContent = "Playing...";

        };


        utterance.onend = () => {

            if (token !== speechToken) {
                return;
            }


            speechIndex++;


            // Small pause between chunks helps browser
            // speech engines complete long explanations.

            setTimeout(() => {

                if (token !== speechToken) return;

                speakNext(token, voice);

            }, 80);

        };


        utterance.onerror = event => {

            if (token !== speechToken) {
                return;
            }


            if (
                event.error === "interrupted" ||
                event.error === "canceled"
            ) {

                return;

            }


            console.error(
                "MediLens speech playback error:",
                event.error
            );


            resetSpeechControls();

            currentUtterance = null;

        };


        window.speechSynthesis.speak(utterance);

    }


    // ============================================
    // 15. PAUSE / RESUME
    // ============================================

    pauseBtn.addEventListener("click", () => {

        if (!("speechSynthesis" in window)) {
            return;
        }


        if (window.speechSynthesis.paused) {

            window.speechSynthesis.resume();

            pauseLabel.textContent = "Pause";


        } else if (window.speechSynthesis.speaking) {

            window.speechSynthesis.pause();

            pauseLabel.textContent = "Resume";

        }

    });


    // ============================================
    // 16. STOP NARRATION
    // ============================================

    stopBtn.addEventListener(
        "click",
        stopSpeech
    );


    function stopSpeech() {

        // Invalidate any currently executing speech callbacks.

        speechToken++;


        if ("speechSynthesis" in window) {

            window.speechSynthesis.cancel();

        }


        speechChunks = [];

        speechIndex = 0;

        currentUtterance = null;


        resetSpeechControls();

    }


    // ============================================
    // 17. RESET SPEECH CONTROLS
    // ============================================

    function resetSpeechControls() {

        speakLabel.textContent = "Listen";

        pauseLabel.textContent = "Pause";

        pauseBtn.hidden = true;

        stopBtn.hidden = true;

    }


    // ============================================
    // 18. CLEANUP
    // ============================================

    window.addEventListener(
        "pagehide",
        stopSpeech
    );


    // ============================================
    // 19. INITIALIZATION COMPLETE
    // ============================================

    console.log(
        "MediLens translation, rich text and narration ready."
    );

});
