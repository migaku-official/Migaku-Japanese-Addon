from aqt import mw
import os
from os.path import dirname, join
from anki.stdmodels import models
from anki.hooks import addHook
from shutil import copyfile




class MILanguageModels():
    def __init__(self, mw):
        self.svg = '''
   <svg class="migaku-logo" width="30" height="39" viewBox="0 0 30 39">
    <path
      fill-rule="evenodd"
      clip-rule="evenodd"
      d="M17.9 25.2947L18.1295 25.4774L18.6805 25.2947H18.956C19.0019 26.254 18.6346 27.2134 17.9918 27.8986C17.6981 28.2537 17.4067 28.6004 17.1201 28.9415C14.4933 32.0665 12.2661 34.7162 12.3903 39C12.3903 39 12.0689 37.2639 11.6557 35.1624C11.4433 34.5836 11.2718 33.9548 11.1 33.3253C10.4178 30.8245 9.73192 28.3106 6.46745 28.858C2.74843 29.3606 0.820054 28.4925 2.10563 25.249C0.661644 23.8747 1.51409 23.5681 2.03641 23.3803C2.27805 23.2934 2.44904 23.2319 2.28929 23.1018C0.178468 22.2675 0.981282 21.3969 1.54393 20.7868C1.87469 20.4281 2.12245 20.1594 1.6465 20.041C-0.235963 19.6298 -0.557358 18.7162 0.957793 17.2543C1.11403 17.0914 1.28714 16.9202 1.46697 16.7423C2.39695 15.8223 3.50664 14.7245 3.39122 13.6909C3.48305 12.3204 3.80444 10.9499 4.2636 9.62504C4.2636 9.53369 4.2636 9.4423 4.3095 9.35095C4.99822 7.66066 5.91649 6.10738 7.11022 4.69118C10.4619 0.396898 16.293 -1.15636 21.3894 0.89942H21.068V1.31058C21.068 1.76741 18.8182 2.90952 18.8182 2.90952L18.8641 2.95517H18.9559V3.00085H18.91L18.91 3.00088H18.8182L18.7723 3.04656L18.6805 3.00088H18.6346L18.5427 2.9552H18.6346L18.6805 2.90952L18.4968 2.86383L18.405 2.90952L18.4509 2.86383H18.3591H18.3132V2.81815L18.2673 2.86383H18.2673H18.1754L18.0836 2.9552H17.9459L17.9918 3.00088L17.9 2.9552L17.8081 3.00088V2.9552L17.7622 3.00088H17.6704L17.7163 3.04656L17.5786 3.00088L17.5327 3.09225H17.4408H17.3949H17.349H17.3031L17.3949 3.13794L17.2572 3.2293H17.2113L17.1194 3.27499H17.0735L17.1194 3.32067H17.0735L16.9817 3.41204H17.0735L16.8898 3.45772L16.9358 3.50341H16.844H16.8439V3.45772L16.6603 3.59477H16.5225V3.68614L16.3848 3.64046L16.4766 3.68614H16.3848H16.2471L16.2011 3.73183H16.1552H16.0634V3.82319H16.1093H16.1552L16.0634 3.86887H16.1552H16.2011L16.293 3.91458L16.3389 3.86887V3.96025L16.2471 4.00593L16.2011 3.96025H16.1093L16.0175 4.00593V4.05161L16.0634 4.00593V4.07118L15.9716 4.09728L16.006 4.13157L15.9716 4.14299H16.0175H16.1093L16.0634 4.18867L16.1552 4.23435H16.3389L16.5225 4.09728H16.6144L16.6603 3.91458L16.7062 4.14299H16.798L16.7521 4.23435L16.8898 4.41709L16.798 4.46276L16.8439 4.59983H17.0276L17.1194 4.50844H17.3031L17.4408 4.32573V4.18867H17.3949L17.5786 4.14299V4.09728L17.6245 4.14299L17.7163 4.09728H17.6245L17.7622 4.00593L17.6245 3.91458H17.5327L17.5786 3.64046L17.6245 3.68614L17.854 3.59477H17.9L18.1295 3.50341L18.0377 3.41204H18.1295V3.36635L18.2213 3.41204V3.36635H18.405L18.5427 3.41204L18.0836 3.68614L18.1754 3.82319L18.1295 3.96025L18.2673 4.00593H18.3591V4.05161L19.0019 4.00593V4.05161L19.2315 4.09728H18.956V4.18867L18.6346 4.14299L18.3591 4.18867L18.4509 4.32573H18.5427V4.50844L18.4509 4.55415L18.2673 4.41709H18.1754L18.0836 4.55415V4.78257H17.9918H17.9V4.82824L17.8081 4.87392L17.854 4.82824L17.7163 4.87392L17.5786 4.78257L17.0735 4.91959V4.96531L16.8439 4.82824L16.5225 4.87392L16.5684 4.82824H16.4307L16.3389 4.73689L16.3848 4.59983L16.6144 4.50844L16.5225 4.46276L16.6144 4.32573L16.293 4.41709L16.2011 4.78257H16.2471L16.293 4.82824H16.2011L16.3848 4.91959L16.2011 4.87392L16.1552 4.96531L16.1093 4.91959H15.9716L16.0175 4.96531H15.7879L15.6961 5.01098H15.6502L15.5584 5.05666L15.5124 4.96531L15.3747 5.10233L15.4665 5.14805H15.2829L15.4206 5.19372L14.9615 5.28507V5.37646L14.9156 5.42214L14.686 5.5592L14.3646 5.46781L14.4105 5.69623H14.1809L14.135 5.65055L13.8595 5.69623L13.9514 5.7419H13.8595V5.83329L14.135 5.87897L14.1809 6.06171H14.3187L14.2728 6.19877V6.24445L14.0432 6.60993H13.079L12.9872 6.56421L12.6658 6.70128L12.7117 6.83834L12.4821 7.29517L12.2526 7.56927L12.3903 7.52359L12.2985 7.66066H12.3444L12.2526 7.93475L12.6658 7.88907L12.8495 8.16316L13.1249 8.02614H13.5841L13.7677 7.8434H13.9973L14.0432 7.70633L14.135 7.66066L14.1809 7.61498L14.135 7.56927L14.0891 7.52359L14.135 7.43224L14.1809 7.38656L14.3646 7.20382L14.8237 7.02108V6.83834L14.9156 6.74696L15.0533 6.70128L15.4206 6.79267L15.9716 6.51854L16.2011 6.60993L16.3389 6.9297L17.2113 7.38656L17.3031 7.61498L17.2113 7.79772H17.3031L17.4408 7.61498L17.5327 7.56927L17.3949 7.43224L17.4867 7.29517H17.6704L17.854 7.43224L17.9 7.38656L17.3949 7.11243L17.4408 7.02108L17.1653 6.97541L16.9358 6.70128L16.7062 6.56421L16.6603 6.3358L16.9358 6.29012L16.9817 6.47286L17.1194 6.38151L17.349 6.74696H17.5327L17.6532 6.82692L17.854 6.88402L17.9918 7.02108L17.9459 7.29517L18.1295 7.38656L18.2673 7.52359H18.3591L18.2673 7.56927L18.3591 7.66066L18.607 7.68806L18.5427 7.66066L18.6346 7.61498V7.52359L18.7264 7.56927L18.5427 7.29517L18.6346 7.2495L18.8641 7.38656L18.8182 7.29517L18.956 7.34085L18.8182 7.20382L19.1855 7.15811L19.507 7.20382L19.4151 7.29517L19.3233 7.38656V7.47791H19.507L19.461 7.66066L19.5529 7.70633H19.461L19.4151 7.66066L19.3692 7.75201L19.5988 7.79772L19.5529 7.8434L19.6906 7.93475L19.6447 7.98042H19.8743L19.6906 8.07181L19.9202 8.02614L20.1956 8.16316H20.3334V8.02614H20.4252L20.7925 8.20888L21.0221 8.11749L21.1139 8.02614H21.3435L21.4812 7.98042V8.20888L21.5731 8.43729L21.2976 9.12254L20.9302 9.16821H20.8384L20.7925 9.07686H20.6089L20.1956 9.2596L19.7365 9.12254H19.3233L19.2315 9.03115L18.8641 8.98547L18.8182 8.89412L18.4968 8.84845L18.1295 9.03115V9.30528L17.9 9.44234L17.6704 9.30528L17.2113 9.16821L17.0735 8.9398L16.6603 8.84845H16.4307L15.9716 8.66571L15.9257 8.57432L16.2011 8.3459L16.0634 8.16316L16.2471 7.98042L16.1093 8.07181L15.9716 7.93475L15.6043 8.02614L15.2829 7.98042L15.0533 8.07181L14.7778 8.02614L14.1809 8.11749L13.9514 8.25455L13.7677 8.30023L13.5382 8.43729H13.3545V8.3459L12.9872 8.39158L12.8495 8.25455L12.7576 8.30023L12.4821 8.66571L11.8853 8.98547L11.7016 9.2596L11.6557 9.53369L11.518 9.71643L11.1966 9.94485L10.9211 9.99053L10.6915 10.2647L10.5078 10.356L10.3242 10.7215L10.0946 10.9042L9.72733 11.4067L9.65385 11.5895L9.72733 11.7722L9.63548 12.0006L9.68138 12.4118L9.45183 12.9143L9.22227 13.1427L9.40592 13.3712V13.5082L9.58958 13.9193L9.72733 13.9651L9.58958 14.0107L9.63548 14.1021L9.68138 14.0564L9.72733 14.2848L9.81914 14.3305L9.91098 14.3762L9.86504 14.4676L9.95688 14.5132V14.7417H10.0487L9.95688 14.7874L10.1405 14.9701V15.0615L10.4619 15.1985L11.0129 15.701L11.2884 15.8381L11.6098 15.6554L12.1148 15.564L12.574 15.7467L13.079 15.5183L13.4922 15.3812L14.0891 15.2442L13.9973 15.3356H14.2268L14.3187 15.3812L14.4105 15.3356L14.3187 15.4269L14.3646 15.4726L14.4564 15.4269L14.3646 15.5183L14.5023 15.7467H14.686V15.6554L14.7319 15.7467V15.6554L14.7778 15.7467L14.8237 15.6554L14.9156 15.7467H15.1451V15.6554L15.237 15.7924L15.3288 15.701L15.4206 15.8838L15.5584 15.8381L15.6043 15.9294H15.5584L15.6043 16.1122L15.4206 16.6147H15.5124V16.7974H15.4665H15.4206L15.463 16.8185L15.4206 17.0716H15.3288L15.5584 17.5284L16.1093 18.0309L16.2471 18.3507L16.3848 18.4421L16.2471 18.4878L16.5684 19.0816L16.4766 19.2644L16.5684 19.4928L16.6603 19.7669L16.6144 20.0867L16.3389 20.4065L16.1552 21.0004V21.5486L16.8439 22.645L16.9817 23.5587L17.5327 24.381L17.7622 24.7465V24.9292L17.6704 25.0205L17.8081 25.3404L17.9 25.2947ZM15.4818 16.8279L15.463 16.8185L15.4665 16.7974L15.4818 16.8279ZM15.4818 16.8279L15.6043 16.8888H15.5124L15.4818 16.8279ZM20.7073 6.19223L20.8384 6.29012H21.0221L20.6548 6.47286L20.517 6.42719L20.4252 6.29012H20.3334L20.517 6.24445L20.4711 6.19877H20.1497L20.1956 6.15306L20.1038 6.10738H20.2875L20.1956 6.06171L20.012 6.10738V6.19877L19.9202 6.29012L19.8743 6.24445L19.9202 6.42719L19.7365 6.47286L19.6906 6.38151V6.6556L19.507 6.83834H19.5988L19.9202 7.11243H19.6447L19.4151 7.29517H19.8743V7.2495H19.9202L19.8743 7.15811L20.2875 7.20382L20.6548 7.02108H20.9762L21.2976 7.20382L21.6649 7.2495H22.0322L22.2158 7.15811L22.2618 7.06676L22.0322 6.88402L21.7108 6.74696L21.068 6.38151L21.2057 6.3358L21.2496 6.16138L21.3435 6.19877L21.2517 6.15306L21.2496 6.16138L21.1139 6.10738H21.2517L21.3435 6.01603L20.7925 6.10738L20.7073 6.19223ZM20.7007 6.19873L20.7073 6.19223L20.7007 6.18732V6.10738L20.6793 6.17133L20.6548 6.15306L20.6777 6.1759L20.6548 6.24445L20.7466 6.3358H20.8384L20.7007 6.19877V6.19873ZM20.7007 6.19873V6.18732L20.6793 6.17133L20.6777 6.1759L20.7007 6.19873ZM16.0175 4.14299L16.1093 4.09728L16.006 4.13157L16.0175 4.14299ZM16.0634 4.07118L16.293 4.00593L16.0634 4.09728V4.07118ZM16.844 3.50341L16.7982 3.59476L16.6604 3.64044V3.59476H16.7522L16.844 3.50341ZM18.7356 7.74289L18.7264 7.75201L18.405 7.70633L18.3591 7.79772L18.4509 8.02614L18.5427 7.98042L18.6346 8.11749V8.02614L18.7723 8.11749L18.6346 7.88907H18.8182L18.7264 7.79772L18.79 7.76608L18.7356 7.74289ZM18.8285 7.7825L18.8641 7.88907V7.79772L18.8285 7.7825ZM19.2776 3.32066L19.2317 3.22929H19.0022L19.2317 3.27497H19.1858L19.2776 3.32066ZM29.1486 11.9092V11.6808L29.0568 11.5438V11.4524H29.0109L28.965 11.361L29.0109 11.3153H28.919L28.965 11.5894L28.8272 11.6808L28.414 11.2697L28.5977 11.224V11.1326L28.414 11.1783L28.2304 10.9956V10.9042L28.1844 10.9499V10.8585H28.1385L28.0926 10.8128V10.8585H28.0467L27.9549 10.6758H27.863L27.7712 10.493L27.0366 10.6301L26.7611 10.5387L26.2561 10.4474L26.0265 10.0819L25.7051 10.2646L25.4755 10.2189L25.2 10.0362L24.9705 9.99052L24.6031 9.53365L24.5572 9.48798L24.4654 9.53365L24.3277 9.39662V9.48798H24.144L24.2358 9.57936L24.144 9.62504H24.2358L24.5113 10.0362L24.8327 10.2646V10.4017L25.0623 10.6758L25.0164 10.4017H25.1541L25.2 10.7671L25.3837 10.8585L25.4755 10.8128H25.7051L26.0265 10.3103V10.493L26.1642 10.7671L26.302 10.9042L26.6234 10.9956L26.8988 11.3153L26.7611 11.7722L26.7152 11.7265L26.6234 11.7722L26.6693 12.092L26.4856 12.1376V12.3204L26.302 12.3661L26.2561 12.5488L25.7969 12.6859L25.751 12.9143L25.4296 13.0513H23.7308V13.0056L23.6849 12.6402L23.1798 11.8636L22.9962 11.6808L22.8125 11.4981L22.7207 11.1783L22.537 10.8585L22.3075 10.7214L22.2156 10.5387L21.6647 9.85346H21.527L21.5729 9.53365L21.481 9.94481L21.2515 9.76211L21.0219 9.4423L21.0678 9.62504L21.2974 9.89913L21.7565 10.6758L21.9402 10.8128H21.8943L21.9861 11.0412L22.3075 11.2697L22.4452 11.4981L22.3993 11.4524L22.4911 12.0463L22.8125 12.229L23.1798 12.96V12.8686L23.2257 12.9143L23.2716 13.0056L23.5012 13.097L24.0522 13.6452L24.0981 13.7366L23.9145 13.8737H24.0522L24.4195 14.1934L24.695 14.0564L24.8327 14.1021L25.0164 14.0107L25.4755 13.965L25.751 13.7823L25.8888 13.8279V14.1934H25.9806L25.7051 14.2848V14.3762V14.5132L25.3378 15.3355C25.5673 15.1985 25.7051 15.2442 25.7969 15.7467C25.9045 16.4156 25.7758 16.9905 25.6599 17.5081C25.5779 17.8742 25.5024 18.2117 25.5214 18.5334C25.5433 18.9028 25.347 19.2205 25.1796 19.4915C24.995 19.7902 24.8456 20.0321 25.0623 20.2237C25.2459 20.4064 25.5673 20.4978 25.8428 20.3608L25.9347 20.2694C25.8888 20.178 26.2101 19.7212 26.3938 19.7669C27.1743 18.7618 27.8171 17.6654 28.2763 16.4776V16.706C28.2763 16.9345 28.2304 17.1629 28.1844 17.3913C28.1385 17.5284 28.2304 17.7111 28.3681 17.7568C28.5058 17.8025 28.6895 17.7111 28.7354 17.5741C29.2404 16.2035 29.5159 14.7873 29.5159 13.3254V12.7772L29.1486 11.9092Z"
      fill="white"
    />
  </svg>'''
        self.mw = mw
        self.modelList = self.getModelList()
        self.style ="""

@font-face {
font-family: yuumichou;
src: url(_yumin.ttf);
}

.card,
.card * {
  box-sizing: border-box;
  padding: 0;
  margin: 0;
  font-family: yuumichou, sans-serif;
}

.card {
  background: #e5f9ff;
  font-size: 18px;
}

.migaku-header {
  background: #2880ff;
  text-align: center;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: center;
  align-items: center;
}

.migaku-header h1 {
  color: white;
}

.migaku-logo {
  height: 53px;
}

.migaku-card {
  background: white;
  width: 90vw;
  max-width: 600px;
  margin: 20px auto 50px;
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.15);
}

.migaku-card-content {
  padding: 20px;
}

.migaku-card--front {
  text-align: center;
}

.migaku-card--back {
  text-align: center;
}

.migaku-word-front {
  font-size: 32px;
}

.migaku-word-back {
  font-size: 24px;
  margin-bottom: 10px;
}

.migaku-card-image img {
  height: 250px;
  width: 90vw;
  max-width: 600px;
  object-fit: cover;
  border-top-right-radius: 10px;
  border-top-left-radius: 10px;
}



.migaku-sentence,
.migaku-translation,
.migaku-definition {
  width: 100%;
  text-align: left;
  margin-top: 20px;
  margin-bottom: 10px;
  font-size: 18px;
  line-height: 19px;
}


.migaku-sentence{
    font-size: 25px;
  line-height: 25px;
}

.migaku-translation{
   margin-top: 10px;
    margin-bottom: 10px;
}

@media (min-width: 762px) {
  .migaku-header {
    justify-content: start;
    padding-left: 50px;
  }
}

@media (min-width: 500px) {
  .migaku-card--back .migaku-card-content {
    display: grid;
    grid-gap: 10px;
    grid-template-areas:
    "word-audio word word word word word word word" "sentence-audio sentence sentence sentence sentence sentence sentence sentence" "translation translation translation translation translation translation translation translation" "definition definition definition definition definition definition definition definition";
  }


  .migaku-card--back .editableField:nth-of-type(1){
     font-size:24px;
  }

  .migaku-card--back .editableField:nth-of-type(3){
     font-size:25px;
  }


  .editableField[data-field="Target Word"]{
    grid-area: word;
  }

  .editableField[data-field="Sentence"]{
    grid-area: sentence;
  }

  .editableField[data-field="Definitions"]{
    grid-area: definition;
  }

  .migakuEditorInput[style]{
    max-width: 570px !important;
  }

  .migakuEditorInput[data-field="Definitions"][style]{
    font-size:18px !important;
  }

  .migakuEditorInput[data-field="Sentence"][style]{
    font-size: 25px !important;
    max-width: 500px !important;
  }

  .migakuEditorInput[data-field="Target Word"][style]{
    font-size: 24px !important;
    max-width: 500px !important;
  }


  .migaku-card--back .migaku-word-audio {
    grid-area: word-audio;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .migaku-card--back .migaku-word-back {
    grid-area: word;
    text-align: left;
  }

  .migaku-card--back .migaku-sentence-audio {
    grid-area: sentence-audio;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .migaku-card--back .migaku-sentence {
    grid-area: sentence;
  }

  .migaku-card--back .migaku-translation {
    grid-area: translation;
  }

  .migaku-card--back .migaku-definition {
    grid-area: definition;
  }
}

.ankidroid_dark_mode.card,
.nightMode.card {
  background: #2b303b;
}

.ankidroid_dark_mode .migaku-header,
.nightMode .migaku-header {
  background: #f9a746;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
}

.ankidroid_dark_mode .migaku-header h1,
.ankidroid_dark_mode .migaku-header h1 {
  color: white;
}

.ankidroid_dark_mode .migaku-card,
.nightMode .migaku-card {
  position: relative;
  background: #363c4a;
  box-shadow: 4px 0px 15px rgba(0, 0, 0, 0.15);
}
"""

    def getModelList(self):
        modelList = []
        name = 'Migaku Japanese Sentence'
        fields = ['Sentence', 'Translation', 'Target Word', 'Definitions', 'Image', 'Sentence Audio', 'Word Audio']
        front = '''<div class="migaku-header">
%s
</div>
<div class="migaku-card migaku-card--front">
    <div class="migaku-card-content">
        <span class="migaku-word-front">{{Sentence}}</span>
    </div>
</div>
'''
        back = '''<div class="migaku-header">
%s
</div>
<div class="migaku-card migaku-card--back">
    <div class="migaku-card-image">
        {{Image}}
    </div>
    <div class="migaku-card-content">
        <div class="migaku-word-back">{{Target Word}}</div>
        <div class="migaku-word-audio">{{Word Audio}}</div>
        <div class="migaku-sentence">{{Sentence}}</div>
        <div class="migaku-sentence-audio">{{Sentence Audio}}</div>
        <div class="migaku-translation ">{{Translation}}</div>
        <div class="migaku-definition">{{Definitions}}</div>
    </div>
</div>
'''
        modelList.append([name, fields, front%self.svg, back%self.svg])
        name = 'Migaku Japanese Vocabulary'
        fields = ['Target Word', 'Sentence', 'Translation', 'Definitions', 'Image', 'Sentence Audio', 'Word Audio']
        front = '''<div class="migaku-header">
%s
</div>
<div class="migaku-card migaku-card--front">
    <div class="migaku-card-content">
        <span class="migaku-word-front">{{Target Word}}</span>
    </div>
</div>
'''

        modelList.append([name, fields, front%self.svg, back%self.svg])
        name = 'Migaku Japanese Audio Sentence'
        fields = ['Sentence', 'Sentence Audio', 'Translation','Target Word', 'Word Audio', 'Definitions', 'Image',]
        front = '''<div class="migaku-header">
%s
</div>
<div class="migaku-card migaku-card--front">
    <div class="migaku-card-content">
        <span class="migaku-word-front">{{Sentence Audio}}</span>
    </div>
</div>
'''

        modelList.append([name, fields, front%self.svg, back%self.svg])
        name = 'Migaku Japanese Audio Vocabulary'
        fields = ['Target Word',  'Sentence', 'Word Audio', 'Sentence Audio', 'Translation', 'Definitions', 'Image']
        front = '''<div class="migaku-header">
%s
</div>
<div class="migaku-card migaku-card--front">
    <div class="migaku-card-content">
        <span class="migaku-word-front">{{Word Audio}}</span>
    </div>
</div>
'''

        modelList.append([name, fields, front%self.svg, back%self.svg])
        return modelList


    def addModels(self):
        config = self.mw.addonManager.getConfig(__name__)
        if config:
            add = False
            if config.get('AddMigakuJapaneseTemplate', False) == "on":
                add = True
            for model in self.modelList:
                if add:
                    self.addModel(model)
            if add:
                self.addExportTemplates()
                self.moveFontToMediaDir('_yumin.ttf')
        


    def addExportTemplates(self):
        addons = self.mw.addonManager.all_addon_meta()
        for addon in addons:
            dirName = addon.dir_name
            if dirName in ["Migaku Dictionary", "1655992655"]:
                self.addExportTemplatesToConfig(dirName)
    
    def addExportTemplatesToConfig(self, dirName):

        templates = {
            "Japanese Sentence": {
              "noteType": "Migaku Japanese Sentence",
              "sentence": "Sentence",
              "secondary": "Translation",
              "notes" : "Definitions",
              "word": "Target Word",
              "image": "Image",
              "audio": "Sentence Audio",
              "unspecified": "Definitions",
              "specific": {
                "Word Audio": [
                  "Forvo"
                ], 
                "Image": 
                ["Google Images"]
              },
              "separator": "<br><br>"
            }, 
            "Japanese Vocabulary": {
              "noteType": "Migaku Japanese Vocabulary",
              "sentence": "Sentence",
              "secondary": "Translation",
              "notes" : "Definitions",
              "word": "Target Word",
              "image": "Image",
              "audio": "Sentence Audio",
              "unspecified": "Definitions",
              "specific": {
                "Word Audio": [
                  "Forvo"
                ], 
                "Image": 
                ["Google Images"]
              },
              "separator": "<br><br>"
            }, 
            "Japanese Audio Sentence": {
              "noteType": "Migaku Japanese Audio Sentence",
              "sentence": "Sentence",
              "secondary": "Translation",
              "notes" : "Definitions",
              "word": "Target Word",
              "image": "Image",
              "audio": "Sentence Audio",
              "unspecified": "Definitions",
              "specific": {
                "Word Audio": [
                  "Forvo"
                ], 
                "Image": 
                ["Google Images"]
              },
              "separator": "<br><br>"
            }, 
            "Japanese Audio Vocabulary": {
              "noteType": "Migaku Japanese Audio Vocabulary",
              "sentence": "Sentence",
              "secondary": "Translation",
              "notes" : "Definitions",
              "word": "Target Word",
              "image": "Image",
              "audio": "Sentence Audio",
              "unspecified": "Definitions",
              "specific": {
                "Word Audio": [
                  "Forvo"
                ], 
                "Image": 
                ["Google Images"]
              },
              "separator": "<br><br>"
            }
        }
        dictConfig = self.mw.addonManager.getConfig(dirName)
        for name, data in templates.items():
            if name not in dictConfig['ExportTemplates']:
                dictConfig['ExportTemplates'][name] = data
        self.mw.addonManager.writeConfig(dirName, dictConfig)
        

    def addModel(self, model):
        if not self.mw.col.models.byName(model[0]):
            modelManager = self.mw.col.models
            newModel = modelManager.new(model[0])
            for fieldName in model[1]:
                field = modelManager.newField(fieldName)
                modelManager.addField(newModel, field)
            template = modelManager.newTemplate('Standard')
            template['qfmt'] = model[2]
            template['afmt'] = model[3]
            newModel['css'] = self.style
            modelManager.addTemplate(newModel, template)
            modelManager.add(newModel)
        
    def moveFontToMediaDir(self, filename):
        src = join(dirname(__file__), filename)
        if os.path.exists(src): 
            path = join(mw.col.media.dir(), filename)
            if not os.path.exists(path): 
                copyfile(src, path)
            return True
        else:
            return False

