// static/js/dashboard-effects.js

function initDashboardEffects() {
    // ===== EFEITO DE FUMAÇA =====
    const canvas = document.getElementById('smokeCanvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    function createSmokeGradient(width, height) {
        const gradient = ctx.createLinearGradient(0, height, 0, 0);
        gradient.addColorStop(0, 'rgba(50, 50, 50, 0.1)');
        gradient.addColorStop(0.3, 'rgba(80, 80, 80, 0.08)');
        gradient.addColorStop(1, 'rgba(120, 120, 120, 0.01)');
        return gradient;
    }

    function generateSmokePattern(width, height) {
        const patternCanvas = document.createElement('canvas');
        patternCanvas.width = width;
        patternCanvas.height = height;
        const patternCtx = patternCanvas.getContext('2d');
        
        const gradient = patternCtx.createRadialGradient(
            width/2, height/2, 0,
            width/2, height/2, Math.max(width, height)/2
        );
        gradient.addColorStop(0, 'rgba(255, 255, 255, 0.8)');
        gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
        
        patternCtx.fillStyle = gradient;
        patternCtx.fillRect(0, 0, width, height);
        
        const imageData = patternCtx.getImageData(0, 0, width, height);
        const data = imageData.data;
        
        for (let i = 0; i < data.length; i += 4) {
            data[i] = data[i] * (0.9 + Math.random() * 0.2);
            data[i + 1] = data[i + 1] * (0.9 + Math.random() * 0.2);
            data[i + 2] = data[i + 2] * (0.9 + Math.random() * 0.2);
            data[i + 3] = data[i + 3] * (0.8 + Math.random() * 0.4);
        }
        
        patternCtx.putImageData(imageData, 0, 0);
        return patternCanvas;
    }

    function animateSmoke() {
        const width = canvas.width;
        const height = canvas.height;
        
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, width, height);
        
        const smokePattern = generateSmokePattern(width, height);
        const smokeGradient = createSmokeGradient(width, height);
        
        ctx.save();
        ctx.globalCompositeOperation = 'lighter';
        
        const time = Date.now() / 4000;
        ctx.translate(
            Math.sin(time * 0.7) * width * 0.05,
            Math.cos(time * 0.5) * height * 0.05 - height * 0.1
        );
        
        ctx.fillStyle = smokeGradient;
        ctx.fillRect(0, 0, width, height);
        
        ctx.globalAlpha = 0.15;
        ctx.drawImage(smokePattern, 0, 0, width, height);
        ctx.restore();
        
        animationFrameId = requestAnimationFrame(animateSmoke);
    }

    // ===== EVENTO DO BOTÃO =====
    function setupButtonEffects() {
        const btn = document.getElementById('estoque-btn');
        if (btn) {
            btn.addEventListener('click', function(event) {
                event.preventDefault();
                setTimeout(() => {
                    window.location = btn.href;
                }, 500);
            });
        }
    }

    // ===== INICIALIZAÇÃO =====
    function init() {
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        setupButtonEffects();
        animateSmoke();
    }

    function cleanup() {
        window.removeEventListener('resize', resizeCanvas);
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
        }
    }

    // Inicializa quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Limpeza quando a página for descarregada
    window.addEventListener('beforeunload', cleanup);
}

// Inicializa os efeitos
initDashboardEffects();