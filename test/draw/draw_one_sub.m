figure;

subplot(1,3,1);
subplot('position', [0.1 0.1 0.22 0.75]);
data = [77.547	78.514	78.377];
b = bar(data,0.6,'FaceColor',[.6 .79 .86]);
xlabel('The times of tests'),
ylabel('Latency(s)')
ylim([0 100])
title('2-block');

subplot(1,3,2);
subplot('position', [0.42 0.1 0.22 0.75]);
data = [72.143	91.047	75.347];
b = bar(data,0.6,'FaceColor',[.97 .67 .55]);
xlabel('The times of tests'),
ylabel('Latency(s)')
title('4-block');

subplot(1,3,3);
subplot('position', [0.74 0.1 0.22 0.75]);
data = [85.924 75.367 94.301];
b = bar(data,0.6,'FaceColor',[.78 .14 .14]);
xlabel('The times of tests'),
ylabel('Latency(s)')
title('4-block-unevenly');

sgtitle('Computational Latency of 1000¡Á1000*1000¡Á1000 Matrix Multiplication')

% figure;
% 
% hold all;
% subplot(1,4,1);
% 
% subplot('position', [0.03 0.1 0.32 0.]);
% data =[102.504 78.146 79.512 85.197];
% X = categorical({'1-block','2-block','4-block','4-block-unevenly'});
% X = reordercats(X,{'1-block','2-block','4-block','4-block-unevenly'});
% b=bar(X,data);
% b.FaceColor = 'flat';
% b.CData(1,:) = [.15 .47 .7];
% b.CData(2,:) = [.6 .79 .86];
% b.CData(3,:) = [.97 .67 .55];
% b.CData(4,:) = [.78 .14 .14];
% 
% xlabel('2-block'),
% ylabel('Latency(s)')
% ylim([0 110])
% 
% subplot(1,4,2);
% subplot('position', [0.4 0.1 0.17 0.8]);
% data = [77.547	78.514	78.377];
% b = bar(data,'FaceColor',[.6 .79 .86]);
% xlabel('2-block'),
% ylabel('Latency(s)')
% ylim([0 110])
% 
% subplot(1,4,3);
% subplot('position', [0.60 0.1 0.17 0.8]);
% data = [72.143	91.047	75.347];
% b = bar(data,'FaceColor',[.97 .67 .55]);
% xlabel('4-block'),
% ylabel('Latency(s)')
% ylim([0 110])
% 
% subplot(1,4,4);
% subplot('position', [0.81 0.1 0.17 0.8]);
% data = [85.924 75.367 94.301];
% b = bar(data,'FaceColor',[.78 .14 .14]);
% xlabel('4-block-unevenly'),
% ylabel('Latency(s)')
% ylim([0 110])
% 
% hold off;
% suptitle('Computational Latency of 1000¡Á1000*1000¡Á1000 Matrix Multiplication')