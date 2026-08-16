// script.js — Griha Pravesh Digital Invitation
// Theme: Temple Gold & Cream — Traditional

document.addEventListener("DOMContentLoaded", function() {

    // ═══════════════════════════════════════
    // 1. DOOR OPEN SEQUENCE
    // ═══════════════════════════════════════
    var doorOverlay = document.getElementById("door-overlay");
    var openBtn = document.getElementById("open-door-btn");
    var skipBtn = document.getElementById("skip-btn");
    var mainContent = document.getElementById("main-content");
    var ambientCanvas = document.getElementById("ambient-canvas");
    var brassKnocker = document.getElementById("brass-knocker");
    var bgMusic = document.getElementById("bg-music");
    var musicToggle = document.getElementById("music-toggle");

    function tryPlayMusic() {
        if (!bgMusic) return;
        bgMusic.volume = 0.3;
        bgMusic.play().then(function() {
            if (musicToggle) {
                musicToggle.classList.add("visible");
                musicToggle.classList.add("playing");
            }
        }).catch(function(err) {
            console.log("Audio blocked:", err);
            if (musicToggle) musicToggle.classList.add("visible");
        });
    }

    function startDoorOpenSequence() {
        if (openBtn.dataset.clicked === "true") return;
        openBtn.dataset.clicked = "true";
        if (skipBtn) skipBtn.style.pointerEvents = "none";

        mainContent.classList.remove("hidden");
        tryPlayMusic();

        // Stage 1: Knocker glows
        doorOverlay.classList.add("knocker-glow");

        // Stage 2: Doors swing open
        setTimeout(function() {
            doorOverlay.classList.add("doors-open");
        }, 400);

        // Stage 3: Flash
        setTimeout(function() {
            doorOverlay.classList.add("flash-out");
        }, 1500);

        // Stage 4: Fade away
        setTimeout(function() {
            doorOverlay.classList.add("fade-away");
        }, 2000);

        // Stage 5: Cleanup
        setTimeout(function() {
            doorOverlay.remove();
            initScrollReveal();
            initAmbientParticles();
            updateCountdown(); // Force countdown update
        }, 2800);
    }

    function skipAnimation() {
        mainContent.classList.remove("hidden");
        doorOverlay.remove();
        initScrollReveal();
        initAmbientParticles();
        updateCountdown();
        if (musicToggle) musicToggle.classList.add("visible");
    }

    if (openBtn) openBtn.addEventListener("click", startDoorOpenSequence);
    if (skipBtn) skipBtn.addEventListener("click", skipAnimation);
    if (brassKnocker) brassKnocker.addEventListener("click", startDoorOpenSequence);

    // Music toggle
    if (musicToggle && bgMusic) {
        musicToggle.addEventListener("click", function() {
            if (bgMusic.paused) {
                bgMusic.play();
                musicToggle.classList.add("playing");
            } else {
                bgMusic.pause();
                musicToggle.classList.remove("playing");
            }
        });
    }

    // ═══════════════════════════════════════
    // 2. QR CODE (Simple Canvas-Based)
    // ═══════════════════════════════════════
    function generateSimpleQR() {
        var qrEl = document.getElementById("qr-venue");
        if (!qrEl) return;
        
        var mapUrl = "https://www.google.com/maps/search/?api=1&query=Mahadevi+Mandira+Mudushedde";
        
        // Create a styled QR placeholder with a map link
        qrEl.style.cssText = "width:120px;height:120px;background:#FFF;border:8px solid #FFF;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.08);display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer;transition:transform 0.3s ease;text-decoration:none;";
        
        // Create a map icon SVG inside
        qrEl.innerHTML = '<svg viewBox="0 0 48 48" width="40" height="40" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M24 4C16.27 4 10 10.27 10 18c0 10.5 14 26 14 26s14-15.5 14-26c0-7.73-6.27-14-14-14z" fill="#6B1D2A" opacity="0.8"/><circle cx="24" cy="18" r="5" fill="#D4AF37"/></svg><span style="font-size:0.6rem;color:#7A6558;margin-top:4px;font-family:Montserrat,sans-serif;letter-spacing:1px;">TAP TO OPEN MAP</span>';
        
        qrEl.addEventListener("click", function() {
            window.open(mapUrl, "_blank", "noopener");
        });
        
        qrEl.addEventListener("mouseenter", function() { qrEl.style.transform = "scale(1.05)"; });
        qrEl.addEventListener("mouseleave", function() { qrEl.style.transform = "scale(1)"; });
    }

    generateSimpleQR();

    // ═══════════════════════════════════════
    // 3. SCROLL REVEAL
    // ═══════════════════════════════════════
    function initScrollReveal() {
        var revealElements = document.querySelectorAll(".scroll-reveal");

        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("active");
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: "0px 0px -40px 0px"
        });

        revealElements.forEach(function(el) { observer.observe(el); });

        // Gold underline draw on section titles
        var titleElements = document.querySelectorAll(".section-title");
        var titleObserver = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("drawn");
                    titleObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        titleElements.forEach(function(el) { titleObserver.observe(el); });
    }

    // ═══════════════════════════════════════
    // 4. COUNTDOWN TIMER
    // ═══════════════════════════════════════
    // Friday 21st August 2026, 10:20 AM IST
    var targetDate = new Date("2026-08-21T10:20:00+05:30").getTime();

    var daysVal = document.getElementById("cd-days");
    var hoursVal = document.getElementById("cd-hours");
    var minsVal = document.getElementById("cd-mins");
    var secsVal = document.getElementById("cd-secs");
    var timerContainer = document.getElementById("countdown-timer");
    var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function setDigit(el, value) {
        if (!el) return;
        var str = value < 10 ? "0" + value : String(value);
        if (el.textContent === str) return;
        el.textContent = str;
        if (reducedMotion) return;
        el.classList.remove("flip");
        void el.offsetWidth;
        el.classList.add("flip");
    }

    function updateCountdown() {
        if (!daysVal) return;
        var now = new Date().getTime();
        var distance = targetDate - now;

        if (distance < 0) {
            if (timerContainer) {
                timerContainer.innerHTML = "<div class='countdown-box' style='width:100%;max-width:300px;'><span class='countdown-val' style='font-size:1rem;padding:10px;font-family:Noto Sans Kannada,sans-serif;'>🏠 ಗೃಹಪ್ರವೇಶ ಸಮಾರಂಭ ಆರಂಭವಾಗಿದೆ!</span></div>";
            }
            return;
        }

        var days = Math.floor(distance / (1000 * 60 * 60 * 24));
        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var mins = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var secs = Math.floor((distance % (1000 * 60)) / 1000);

        setDigit(daysVal, days);
        setDigit(hoursVal, hours);
        setDigit(minsVal, mins);
        setDigit(secsVal, secs);
    }

    // Start countdown immediately
    updateCountdown();
    setInterval(updateCountdown, 1000);

    // ═══════════════════════════════════════
    // 5. AMBIENT PARTICLES (Marigold Petals & Gold Dust)
    // ═══════════════════════════════════════
    var particleAnimationId;

    function initAmbientParticles() {
        if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || !ambientCanvas) return;

        var ctx = ambientCanvas.getContext("2d");
        var particles = [];
        var maxParticles = 28;

        var colors = [
            "rgba(232, 168, 48, 0.45)",
            "rgba(240, 192, 64, 0.35)",
            "rgba(203, 163, 88, 0.3)",
            "rgba(226, 61, 40, 0.2)",
            "rgba(212, 175, 55, 0.35)"
        ];

        function resizeCanvas() {
            ambientCanvas.width = Math.min(ambientCanvas.parentElement ? ambientCanvas.parentElement.clientWidth : 480, 480);
            ambientCanvas.height = window.innerHeight;
        }

        window.addEventListener("resize", resizeCanvas);
        resizeCanvas();

        for (var i = 0; i < maxParticles; i++) {
            var isPetal = Math.random() > 0.45;
            particles.push({
                x: Math.random() * ambientCanvas.width,
                y: Math.random() * ambientCanvas.height,
                radius: isPetal ? (Math.random() * 4 + 2) : (Math.random() * 2 + 0.5),
                speedX: Math.random() * 0.4 - 0.2,
                speedY: Math.random() * 0.4 + 0.12,
                opacity: Math.random() * 0.4 + 0.15,
                wobble: Math.random() * Math.PI * 2,
                wobbleSpeed: Math.random() * 0.015 + 0.004,
                color: colors[Math.floor(Math.random() * colors.length)],
                isPetal: isPetal,
                rotation: Math.random() * Math.PI * 2,
                rotationSpeed: (Math.random() - 0.5) * 0.025
            });
        }

        function drawParticles() {
            ctx.clearRect(0, 0, ambientCanvas.width, ambientCanvas.height);

            for (var i = 0; i < maxParticles; i++) {
                var p = particles[i];
                ctx.save();
                ctx.globalAlpha = p.opacity;
                ctx.fillStyle = p.color;

                if (p.isPetal) {
                    ctx.translate(p.x, p.y);
                    ctx.rotate(p.rotation);
                    ctx.beginPath();
                    ctx.ellipse(0, 0, p.radius, p.radius * 0.45, 0, 0, Math.PI * 2);
                    ctx.closePath();
                    ctx.fill();
                    p.rotation += p.rotationSpeed;
                } else {
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                    ctx.closePath();
                    ctx.fill();
                }

                ctx.restore();

                p.y += p.speedY;
                p.wobble += p.wobbleSpeed;
                p.x += p.speedX + Math.sin(p.wobble) * 0.25;

                if (p.y > ambientCanvas.height) {
                    p.y = -10;
                    p.x = Math.random() * ambientCanvas.width;
                    p.opacity = Math.random() * 0.4 + 0.15;
                }
                if (p.x > ambientCanvas.width) p.x = 0;
                else if (p.x < 0) p.x = ambientCanvas.width;
            }

            particleAnimationId = requestAnimationFrame(drawParticles);
        }

        drawParticles();

        document.addEventListener("visibilitychange", function() {
            if (document.hidden) cancelAnimationFrame(particleAnimationId);
            else drawParticles();
        });
    }

    // ═══════════════════════════════════════
    // 6. CALENDAR .ICS
    // ═══════════════════════════════════════
    var downloadIcsBtn = document.getElementById("download-ics-btn");

    if (downloadIcsBtn) {
        downloadIcsBtn.addEventListener("click", function() {
            var icsContent = [
                "BEGIN:VCALENDAR",
                "VERSION:2.0",
                "PRODID:-//Maya//Griha Pravesh//EN",
                "CALSCALE:GREGORIAN",
                "BEGIN:VEVENT",
                "SUMMARY:ಗೃಹಪ್ರವೇಶ — ಮಾತೃಭಾಯಾ | Griha Pravesh",
                "UID:uid-grihapravesh-2026@maya",
                "DTSTART:20260821T045000Z",
                "DTEND:20260821T073000Z",
                "LOCATION:Mahadevi Mandira\\, Mudushedde",
                "DESCRIPTION:Griha Pravesh & Sri Satyanarayana Pooja at 10:20 AM\\nLunch at 1:00 PM\\nHosts: Sri Vishwanath & Srimathi Jalajakshy\\nVenue: Mahadevi Mandira\\, Mudushedde",
                "END:VEVENT",
                "END:VCALENDAR"
            ].join("\r\n");

            var blob = new Blob([icsContent], { type: "text/calendar;charset=utf-8" });
            var link = document.createElement("a");
            link.href = window.URL.createObjectURL(blob);
            link.setAttribute("download", "Griha_Pravesh_Matrubhaya.ics");
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    }

});
