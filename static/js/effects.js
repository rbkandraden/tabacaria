// static/js/effects.js

document.addEventListener('DOMContentLoaded', function() {
    // Sistema de Fumaça Aprimorado
    function createSmoke(event) {
        const btn = event.currentTarget;
        const btnRect = btn.getBoundingClientRect();
        
        const centerX = btnRect.left + (btnRect.width / 2);
        const centerY = btnRect.top + (btnRect.height / 2);

        for(let i = 0; i < 8; i++) {
            const smoke = document.createElement('div');
            smoke.className = 'smoke-particle';
            
            smoke.style.left = `${centerX + (Math.random() - 0.5) * 50}px`;
            smoke.style.top = `${centerY + (Math.random() - 0.5) * 30}px`;
            smoke.style.animationDuration = `${1 + Math.random() * 1.5}s`;
            smoke.style.background = `rgba(255, 255, 255, ${0.5 + Math.random() * 0.3})`;
            smoke.style.width = `${8 + Math.random() * 8}px`;
            smoke.style.height = smoke.style.width;
            
            document.body.appendChild(smoke);
            
            setTimeout(() => {
                smoke.remove();
            }, 2000);
        }
    }

    // Aplica a todos os botões com classe .smoke-btn
    document.querySelectorAll('.smoke-btn').forEach(btn => {
        btn.addEventListener('click', createSmoke);
    });

    // Efeito hover glow
    document.querySelectorAll('[data-hover="glow"]').forEach(el => {
        el.addEventListener('mouseenter', () => {
            el.style.filter = 'drop-shadow(0 0 8px rgba(255, 255, 255, 0.3))';
        });
        el.addEventListener('mouseleave', () => {
            el.style.filter = 'none';
        });
    });
});