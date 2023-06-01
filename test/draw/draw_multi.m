% ÑÕÉ«¶¨Òå
C1 = '#2878b5'; 
C2 = '#9ac9db';
C3 = '#f8ac8c';
C4 = '#c82423';

y=[102.504 78.146;140.274 103.017; 217.35 164.503; 414.136 334.273;];
figure
b=bar(y);



title('Computational Latency of Matrix Multiplication')
xlabel('Matrix multiplication')
ylabel('Latency(s)')
xticklabels({'1000¡Á1000*1000¡Á1000','1200¡Á1000*1000¡Á1200','1500¡Á1000*1000¡Á1500','2000¡Á1000*1000¡Á2000'})
xtickangle(8)

legend({'computing', 'block-computing'},'Location','northwest')