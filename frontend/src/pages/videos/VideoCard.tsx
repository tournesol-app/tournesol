import React from 'react';
import makeStyles from '@mui/styles/makeStyles';
import { useParams } from 'react-router-dom';
import { VideoCardFromId } from 'src/features/videos/VideoCard';
import { useVideoMetadata } from 'src/features/videos/VideoApi';
import Container from '@mui/material/Container';
import { allCriterias } from 'src/utils/constants';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis } from 'recharts';

const renderCustomAxisTick = ({ x, y, payload }: any) => {
  const paths: any = {
    backfire_risk:
      'M19.4253 2.0229C21.3288 2.87466 23.1112 3.67225 24.5309 3.67225C24.8138 3.67225 25.0851 3.78462 25.2851 3.98463C25.4851 4.18465 25.5975 4.45594 25.5975 4.73881V11.0529C25.5975 19.1907 20.5313 23.169 16.8197 26.07C16.6813 26.1693 16.5415 26.2722 16.3999 26.3763C15.3464 27.1515 14.1931 28 12.7881 28C11.3895 28 10.2414 27.1619 9.18881 26.3936C9.043 26.2871 8.89902 26.1821 8.75647 26.0807L8.73072 26.0604C5.04265 23.1505 0 19.1718 0 11.0529V4.73881C0 4.45594 0.11237 4.18465 0.312389 3.98463C0.512408 3.78462 0.783692 3.67225 1.06656 3.67225C2.64444 3.67225 4.48223 2.83479 6.40254 1.95972C8.50343 1.00237 10.7031 0 12.7693 0C14.9045 0 17.2444 1.047 19.4253 2.0229ZM9.53305 9.92678C9.85435 9.92678 10.165 10.0331 10.4089 10.2265L11.8989 11.4874L15.0864 8.80705C15.3277 8.60868 15.6394 8.4991 15.9623 8.4991C16.2852 8.4991 16.5968 8.60868 16.8382 8.80705L19.0415 10.6273C19.1662 10.7337 19.2658 10.8628 19.3339 11.0065C19.402 11.1502 19.4372 11.3054 19.4372 11.4623C19.4372 11.6192 19.402 11.7744 19.3339 11.9181C19.2658 12.0619 19.1662 12.191 19.0415 12.2973L12.8289 17.5243C12.5813 17.7296 12.2585 17.8401 11.926 17.8333C11.5928 17.8436 11.2686 17.7326 11.023 17.5243L6.50806 13.7251C6.38048 13.6203 6.27832 13.4917 6.20829 13.3478C6.13826 13.2039 6.10194 13.048 6.10172 12.8901C6.10352 12.7334 6.13965 12.5786 6.20794 12.435C6.27622 12.2915 6.37524 12.1623 6.49903 12.0552L8.65716 10.2265C8.90105 10.0331 9.21174 9.92678 9.53305 9.92678Z',
    better_habits:
      'M19.0392 5.71703C21.1745 6.03733 22.9895 7.05159 24.3241 8.75983C25.6052 10.3613 26.2458 12.2297 26.1924 14.2582C26.1391 15.6995 25.9789 17.1409 25.6052 18.5288C24.7511 21.625 23.1496 24.3475 20.8008 26.4828C19.3595 27.764 17.6513 28.191 15.7295 27.9241C14.9288 27.8173 14.1814 27.5504 13.3807 27.3369C13.2205 27.2835 13.0604 27.2835 12.9002 27.3369C12.313 27.4971 11.7258 27.6572 11.1386 27.764C9.11007 28.2444 7.29507 27.8707 5.64022 26.5362C4.99963 26.0557 4.51919 25.4685 3.98536 24.8279C2.43727 23.0129 1.36963 20.931 0.675654 18.6356C0.301977 17.4078 0.0884472 16.1266 0.0350648 14.8454C-0.0183176 14.0447 -0.0183185 13.2973 0.0884464 12.4966C0.408741 10.5214 1.31624 8.86659 2.81095 7.58542C4.67933 5.93056 6.92139 5.34335 9.37698 5.5035C10.2845 5.55688 11.192 5.71703 12.0995 5.93056C12.2596 5.98394 12.313 5.93056 12.313 5.77041C12.313 5.45012 12.2596 5.07644 12.2063 4.75615C11.886 3.42159 11.1386 2.35394 9.91081 1.65997C9.6439 1.49982 9.6439 1.49982 9.80405 1.23291C9.96419 0.912616 10.1243 0.592321 10.2845 0.272026C10.3379 0.111879 10.4446 0.111879 10.5514 0.165262C10.7649 0.325409 10.9785 0.432173 11.192 0.592321C12.0461 1.17953 12.6867 1.92688 13.1671 2.83438C13.2739 2.99453 13.2739 2.99453 13.3807 2.83438C13.5408 2.56747 13.7543 2.35394 13.9679 2.14041C15.3024 0.752468 16.9573 0.0584965 18.8791 0.00511407C20.0001 -0.0482683 21.0144 0.325409 22.082 0.699086C22.1888 0.752468 22.1888 0.805851 22.1354 0.912615C21.6016 1.71335 21.0677 2.46071 20.3204 3.10129C19.0926 4.11556 17.6513 4.70277 15.9964 4.75615C15.2491 4.75615 14.5551 4.64938 13.8611 4.43585C13.7543 4.38247 13.701 4.38247 13.701 4.54262C13.8077 4.96968 13.8611 5.39674 13.8077 5.77041C13.8077 5.87718 13.8611 5.87718 13.9679 5.87718C15.1423 5.55688 16.3701 5.39674 17.8114 5.39674C18.1317 5.61027 18.5588 5.66365 19.0392 5.71703ZM7.66875 8.75983C6.44095 8.91998 5.42669 9.4538 4.57257 10.3613C3.66507 11.3222 3.18463 12.4432 3.13124 13.7778C3.13124 14.0981 3.18463 14.4184 3.45154 14.6319C3.71845 14.8454 3.98536 14.8454 4.30566 14.6853C4.57257 14.5251 4.73272 14.3116 4.73272 13.9913C4.73272 13.5642 4.7861 13.1906 4.94625 12.8169C5.48007 11.3222 6.81463 10.3613 8.46949 10.3079C8.89655 10.3079 9.16345 10.041 9.21684 9.66733C9.27022 9.24027 9.05669 8.86659 8.68301 8.75983C8.52286 8.70645 8.4161 8.75983 8.25596 8.70645C8.04243 8.70645 7.88228 8.75983 7.66875 8.75983Z',
    diversity_inclusion:
      'M12.3001 3.02727C10.691 4.63636 9.70921 6.65455 9.40921 8.75455C7.06376 8.97273 4.82739 9.95455 3.02739 11.7545C-1.00897 15.7909 -1.00897 22.3909 3.0274 26.4273C7.06376 30.4636 13.6638 30.4636 17.7001 26.4273C19.3092 24.8182 20.291 22.8 20.6183 20.6727C22.9365 20.4818 25.2001 19.4727 26.9728 17.7C31.0092 13.6636 31.0092 7.06364 26.9729 3.02727C22.9365 -1.00909 16.3365 -1.00909 12.3001 3.02727ZM18.3547 18.3C16.7456 18.0545 15.1638 17.2909 13.9092 16.0364C12.5456 14.6727 11.7547 12.9 11.591 11.1C11.5638 10.6909 11.5638 10.3091 11.5638 9.92727C13.5001 10.1727 15.3547 11.0455 16.8547 12.5455C18.491 14.1818 19.3638 16.2545 19.5274 18.3818C19.1456 18.3818 18.7638 18.3818 18.3547 18.3ZM16.0365 24.7636C12.9001 27.9 7.77285 27.9 4.63649 24.7636C1.50012 21.6273 1.50012 16.5 4.63649 13.3636C5.94558 12.0545 7.58194 11.2909 9.27285 11.0727C9.43649 13.4727 10.4456 15.8455 12.2728 17.6727C13.9365 19.3364 16.0638 20.3182 18.2183 20.6182C17.9456 22.1455 17.2092 23.5909 16.0365 24.7636Z',
    pedagogy:
      'M30.9461 9.27871L18.5545 15.4729C17.1493 16.1766 14.8483 16.1766 13.4442 15.4729L1.05469 9.27871C-0.351562 8.57506 -0.351562 7.42402 1.05469 6.72247L13.4442 0.526161C14.8494 -0.175387 17.1493 -0.175387 18.5545 0.526161L30.9461 6.72247C32.3513 7.42402 32.3513 8.57506 30.9461 9.27871ZM18.5787 8.00059C18.5787 7.15726 17.4234 6.47252 15.9993 6.47252C14.5752 6.47252 13.42 7.15726 13.42 8.00059C13.42 8.84392 14.5752 9.52866 15.9993 9.52866C17.4234 9.52866 18.5787 8.84392 18.5787 8.00059ZM30.9606 19.5205C30.9606 18.862 30.5668 18.298 30.0028 18.0418V11.2479L28.6648 11.9169V18.0418C28.1009 18.298 27.707 18.862 27.707 19.5205C27.707 19.9353 27.8667 20.3081 28.1208 20.5949L26.9204 24.4817C26.9204 24.4817 27.6272 25.2757 29.3349 25.2757C31.0415 25.2757 31.7493 24.4817 31.7493 24.4817L30.5479 20.5949C30.802 20.3081 30.9606 19.9343 30.9606 19.5205ZM26.9195 12.7886L19.1521 16.6712C18.2909 17.1018 17.1692 17.3402 15.9982 17.3402C14.8262 17.3402 13.7046 17.1018 12.8423 16.6712L5.07699 12.7886V18.8274C5.07699 20.8742 10.367 23.5187 15.9972 23.5187C21.6274 23.5187 26.9174 20.8742 26.9174 18.8274C26.9195 17.648 26.9195 14.9069 26.9195 12.7886Z',
    largely_recommended:
      'M23.1323 14.5542C23.6379 13.7961 24.4603 13.2911 25.4098 13.2921C26.8656 13.2936 28.0695 14.496 27.9443 15.8868L27.9518 23.2208C27.9542 25.5601 27.0069 27.772 25.3629 29.4141C23.7189 31.1195 21.5043 32.0024 19.1623 32L14.9846 31.9957C12.0096 31.9927 9.22311 30.6622 7.32184 28.3842L0.603997 20.2847C0.160331 19.7152 -0.0936377 18.9563 0.0321866 18.1977C0.0947127 17.4391 0.537157 16.8073 1.16969 16.3654C2.24505 15.671 3.70104 15.799 4.58811 16.685L7.31264 19.3432C7.376 19.4065 7.56596 19.4699 7.6925 19.4068C7.88233 19.3438 7.94549 19.2174 7.94537 19.0909L7.92864 2.6527C7.92716 1.19855 9.1286 -0.00147836 10.5845 1.367e-06C11.344 0.00077377 11.9773 0.254311 12.4842 0.760617C12.9911 1.26692 13.245 1.96264 13.2457 2.65811L13.2548 11.6359C13.7604 10.8777 14.5828 10.3728 15.5323 10.3737C16.9881 10.3752 18.192 11.5777 18.1935 13.0318L18.1936 13.0951C18.6992 12.3369 19.5215 11.8319 20.471 11.8329C21.9269 11.8344 23.1308 13.0369 23.1322 14.491L23.1323 14.5542ZM17.4184 17.5028C17.2367 17.1345 16.7114 17.1345 16.5296 17.5028L15.3051 19.9839C15.2329 20.1302 15.0934 20.2316 14.932 20.255L12.1939 20.6529C11.7874 20.712 11.6251 21.2115 11.9192 21.4982L13.9005 23.4295C14.0173 23.5434 14.0706 23.7074 14.0431 23.8682L13.5753 26.5952C13.5059 27 13.9308 27.3087 14.2944 27.1176L16.7434 25.8301C16.8878 25.7542 17.0603 25.7542 17.2046 25.8301L19.6536 27.1176C20.0172 27.3087 20.4422 27 20.3727 26.5952L19.905 23.8682C19.8774 23.7074 19.9307 23.5434 20.0475 23.4295L22.0288 21.4982C22.323 21.2115 22.1606 20.712 21.7542 20.6529L19.0161 20.255C18.8547 20.2316 18.7151 20.1302 18.6429 19.9839L17.4184 17.5028Z',
    engaging:
      'M25.28 14.0655L27.6006 18.4956C28.1721 19.5871 27.632 20.48 26.4 20.48H25.28V24.4C25.28 25.632 24.272 26.64 23.04 26.64H19.96V30H7.36V20.3957C5.29304 18.4548 4 15.699 4 12.6397C4 6.76364 8.76364 2 14.64 2C20.5164 2 25.28 6.76392 25.28 12.64V14.0655ZM15.846 15.3613L16.255 14.6515L15.4458 13.7113L15.5744 12.9822L16.6571 12.3746L16.5143 11.5682L15.2899 11.3677L14.9197 10.7262L15.3582 9.56532L14.7307 9.03892L13.6639 9.67284L12.9681 9.41972L12.5582 8.2482H11.7389L11.329 9.41972L10.6332 9.67284L9.56612 9.03892L8.93864 9.5656L9.3774 10.7265L9.00724 11.3674L7.78224 11.5679L7.64 12.3748L8.72276 12.9819L8.85128 13.711L8.0418 14.6521L8.45144 15.3613L9.67112 15.1306L10.2381 15.6063L10.2224 16.8478L10.9924 17.1278L11.7784 16.1669H12.519L13.305 17.1278L14.0744 16.8473L14.059 15.6063L14.6266 15.1306L15.846 15.3613ZM20.6888 11.0602L21.0985 10.3507L20.3402 9.49588V8.91152L21.0988 8.0564L20.6891 7.34688L19.5697 7.57592L19.0632 7.28388L18.7022 6.2H17.883L17.5212 7.28416L17.0152 7.5762L15.8952 7.34716L15.4856 8.05668L16.2441 8.91152V9.49588L15.4856 10.3507L15.8952 11.0602L17.0147 10.8312L17.5212 11.1235L17.8827 12.2074H18.702L19.0629 11.1235L19.5688 10.8312L20.6888 11.0602ZM18.2926 9.95763C18.7091 9.95763 19.0467 9.62003 19.0467 9.20359C19.0467 8.78714 18.7091 8.44955 18.2926 8.44955C17.8762 8.44955 17.5386 8.78714 17.5386 9.20359C17.5386 9.62003 17.8762 9.95763 18.2926 9.95763ZM12.1486 13.8252C12.7404 13.8252 13.2201 13.3455 13.2201 12.7537C13.2201 12.1618 12.7404 11.6821 12.1486 11.6821C11.5568 11.6821 11.077 12.1618 11.077 12.7537C11.077 13.3455 11.5568 13.8252 12.1486 13.8252Z',
    entertaining_relaxing:
      'M0 15C0 6.729 6.729 0 15 0C23.271 0 30 6.729 30 15C30 23.271 23.271 30 15 30C6.729 30 0 23.271 0 15ZM10.875 12.1238C11.0143 12.588 11.4399 12.888 11.901 12.888C12.003 12.888 12.1067 12.8734 12.2087 12.8426C12.7757 12.6728 13.0972 12.0758 12.9275 11.5088C12.516 10.1366 11.2826 9.21427 9.8576 9.21427C8.4326 9.21427 7.19874 10.1361 6.78774 11.5088C6.61803 12.0754 6.93946 12.6728 7.50646 12.8426C8.07217 13.0114 8.67046 12.6904 8.84017 12.1238C8.97817 11.6648 9.3866 11.3567 9.8576 11.3567C10.3286 11.3567 10.7375 11.6648 10.875 12.1238ZM22.1851 12.888C21.7239 12.888 21.2983 12.588 21.1591 12.1239C21.0215 11.6653 20.6131 11.3567 20.1421 11.3567C19.6711 11.3567 19.2622 11.6653 19.1246 12.1243C18.9545 12.6913 18.3562 13.0123 17.7909 12.8426C17.2239 12.6729 16.9025 12.0754 17.0722 11.5084C17.4836 10.1362 18.7175 9.21387 20.1421 9.21387C21.5671 9.21387 22.8005 10.1362 23.2115 11.5089C23.3812 12.0759 23.0598 12.6729 22.4923 12.8426C22.3908 12.8734 22.2866 12.888 22.1851 12.888ZM21.5373 18.75H8.46288C7.78421 18.75 7.31737 19.3579 7.56919 19.9162C8.74701 22.5289 11.63 24.375 14.9999 24.375C18.3702 24.375 21.2528 22.5289 22.4307 19.9162C22.6828 19.3579 22.216 18.75 21.5373 18.75Z',
    layman_friendly:
      'M15.561 8.23625C15.561 3.67931 19.2403 0 23.7973 0C28.3542 0 32.0335 3.67931 31.9998 8.23625C31.9998 12.7932 28.3205 16.4725 23.7635 16.4725C22.4471 16.4725 21.1306 16.1687 19.9829 15.5611L15.9323 16.8101C15.8648 16.8438 15.8311 16.8438 15.7635 16.8438C15.6285 16.8438 15.4598 16.7763 15.3585 16.675C15.2235 16.54 15.156 16.3037 15.2235 16.1012L16.4724 12.0168C15.8648 10.8354 15.561 9.5527 15.561 8.23625ZM23.831 10.8692L27.5441 7.15609C27.9492 6.71727 27.9492 6.00841 27.5441 5.60335C27.1053 5.16453 26.4302 5.16453 25.9914 5.60335L23.0547 8.54005L21.8732 7.35862C21.4344 6.9198 20.7593 6.9198 20.3205 7.35862C19.8817 7.79743 19.8817 8.47254 20.3205 8.91135L22.2783 10.8692C22.4808 11.0717 22.7846 11.1729 23.0547 11.1729C23.3247 11.1729 23.6285 11.0717 23.831 10.8692ZM8.03366 17.5527C10.7368 17.5527 12.9282 15.3613 12.9282 12.6582C12.9282 9.95503 10.7368 7.76369 8.03366 7.76369C5.33051 7.76369 3.13917 9.95503 3.13917 12.6582C3.13917 15.3613 5.33051 17.5527 8.03366 17.5527ZM13.9409 18.9704C13.4008 18.5991 12.5569 18.3291 11.578 18.1603C10.5654 18.8016 9.35017 19.1729 8.06748 19.1729C6.78478 19.1729 5.5696 18.8016 4.55694 18.1603C3.54429 18.3291 2.70041 18.5991 2.19408 18.9704C0.236286 20.3206 0.0337551 24.54 0 25.3501C0 25.5864 0.101265 25.8565 0.270041 26.0252C0.438817 26.194 0.708858 26.2953 0.945144 26.2953H15.1898C15.4598 26.2953 15.6961 26.194 15.8649 26.0252C16.0337 25.8565 16.135 25.5864 16.135 25.3501C16.1012 24.54 15.8987 20.2869 13.9409 18.9704Z',
    reliability:
      'M11.0749 7.2C11.6051 7.2 12.0349 6.77019 12.0349 6.24C12.0349 5.70981 11.6051 5.28 11.0749 5.28C10.5447 5.28 10.1149 5.70981 10.1149 6.24C10.1149 6.77019 10.5447 7.2 11.0749 7.2Z',
  };
  console.log(payload);
  return (
    <svg
      x={x - 12}
      y={y - 12}
      width="26"
      height="28"
      viewBox="0 0 26 28"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d={paths[payload.value]}
        fill="#D37A80"
      />
    </svg>
  );
};

const useStyles = makeStyles(() => ({
  root: {
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    minWidth: '420px',
    marginTop: 120,
  },
}));

function VideoCardPage() {
  const classes = useStyles();
  const { video_id } = useParams<{ video_id: string }>();
  const video = useVideoMetadata(video_id);

  const shouldDisplayChart =
    video.criteria_scores && video.criteria_scores.length > 0;

  const data: any = shouldDisplayChart ? video.criteria_scores : null;

  return (
    <div>
      <div className={classes.root}>
        <VideoCardFromId videoId={video_id} />
      </div>
      {shouldDisplayChart && (
        <Container maxWidth="sm">
          <RadarChart width={600} height={300} outerRadius="80%" data={data}>
            <PolarGrid />
            <PolarAngleAxis dataKey="criteria" tick={renderCustomAxisTick} />
            <Radar
              dataKey="score"
              stroke="#8884d8"
              fill="#8884d8"
              fillOpacity={0.6}
            />
          </RadarChart>
        </Container>
      )}
    </div>
  );
}

export default VideoCardPage;
