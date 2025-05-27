function [band_powers, dominant_band, mental_state] = process_eeg(mat_file)
 
    try
        data = load(mat_file);
    catch ME
        error('Error loading .mat file: %s', ME.message);
    end
    if ~isfield(data, 'o')
        error('Structure ''o'' not found in %s.', mat_file);
    end
    o = data.o;
    eeg = o.data;
    if iscell(eeg)
        eeg = eeg{1};
    end
    Fs = 1000;
    eeg = double(eeg(:));
    N = length(eeg);
    Y = fft(eeg);
    f = (0:N-1)*(Fs/N);
    P = abs(Y).^2 / N;
    f_half = f(1:floor(N/2));
    P_half = P(1:floor(N/2));
    % Frequency bands
    bands = {
        'Delta', 0.5, 4;
        'Theta', 4, 8;
        'Alpha', 8, 13;
        'Beta', 13, 30;
        'Gamma', 30, 100;
    };
    num_bands = size(bands, 1);
    band_powers = zeros(num_bands, 1);
    for i = 1:num_bands
        idx = find(f_half >= bands{i,2} & f_half <= bands{i,3});
        band_powers(i) = sum(P_half(idx));
    end
    [~, dominant_band_index] = max(band_powers);
    dominant_band = bands{dominant_band_index, 1};
    % Interpretation
    switch dominant_band
        case 'Delta'
            mental_state = 'Deep sleep or pathological condition';
        case 'Theta'
            mental_state = 'Drowsiness or meditative state';
        case 'Alpha'
            mental_state = 'Relaxed wakefulness (eyes closed)';
        case 'Beta'
            mental_state = 'Alertness and concentration';
        case 'Gamma'
            mental_state = 'High-level cognition and sensory processing';
        otherwise
            mental_state = 'Unclear';
    end

    oneDrivePath = "C:\Users\santh.UNNIMAYA\OneDrive"; %%%please mention path of your device for the code to work
    resultsFilename = fullfile(oneDrivePath, 'eeg_results.txt');
    powerSpectrumFilename = fullfile(oneDrivePath, 'eeg_power.png');
    bandDecompositionFilename = fullfile(oneDrivePath, 'eeg_bands.png');
 
    figure('Visible', 'off');
    plot(f_half, P_half);
    xlabel('Frequency (Hz)');
    ylabel('Power');
    title('Power Spectrum');
    grid on;
    saveas(gcf, powerSpectrumFilename); 
    figure('Visible', 'off');
    bar(band_powers);
    set(gca, 'XTickLabel', bands(:,1));
    ylabel('Power      ');
    title('Band Decomposition');
    grid on;
    saveas(gcf, bandDecompositionFilename); 
    fid = fopen(resultsFilename, 'w'); 
    for i = 1:num_bands
        fprintf(fid, '%s: %.6f\n', bands{i, 1}, band_powers(i));
    end
    fprintf(fid, 'Dominant Band: %s\n', dominant_band);
    fprintf(fid, 'Mental State: %s\n', mental_state);
    fclose(fid);
end