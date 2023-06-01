
X = categorical({'1-block','2-block','4-block','4-block-unevenly'});
X = reordercats(X,{'1-block','2-block','4-block','4-block-unevenly'});
Y=[102.504 78.146 79.512 85.197];
b=bar(X,Y,0.4);

title('Computational Latency of 1000¡Á1000*1000¡Á1000 Matrix Multiplication')
xlabel('Matrix multiplication')
ylabel('Latency(s)')

b.FaceColor = 'flat';
b.CData(1,:) = [.15 .47 .7];
b.CData(2,:) = [.6 .79 .86];
b.CData(3,:) = [.97 .67 .55];
b.CData(4,:) = [.78 .14 .14];
