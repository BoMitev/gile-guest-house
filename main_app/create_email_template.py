from hotel_gile import settings

HEAD = """
<html lang="en"">
    <head>
      <meta charset="utf8">
      <meta http-equiv="x-ua-compatible" content="ie=edge">
      <meta name="viewport" content="width=device-width,initial-scale=1">
      <meta name="x-apple-disable-message-reformatting">
      <title>Your reservation is now confirmed</title>
      <style>
        @media screen {
          img {
            max-width: 100%;
          }
          td,
          th {
            box-sizing: border-box;
          }
          u~div .wrapper {
            min-width: 100vw;
          }
          a[x-apple-data-detectors] {
            color: inherit;
            text-decoration: none;
          }
          .all-font-roboto {
            font-family: Roboto, -apple-system, "Segoe UI", sans-serif !important;
          }
          .all-font-sans {
            font-family: -apple-system, "Segoe UI", sans-serif !important;
          }
        }
        @media (max-width: 600px) {
          .sm-inline-block {
            display: inline-block !important;
          }
          .sm-hidden {
            display: none !important;
          }
          .sm-leading-32 {
            line-height: 32px !important;
          }
          .sm-p-20 {
            padding: 20px !important;
          }
          .sm-py-12 {
            padding-top: 12px !important;
            padding-bottom: 12px !important;
          }
          .sm-text-center {
            text-align: center !important;
          }
          .sm-text-xs {
            font-size: 12px !important;
          }
          .sm-text-lg {
            font-size: 18px !important;
          }
          .sm-w-1-4 {
            width: 25% !important;
          }
          .sm-w-3-4 {
            width: 75% !important;
          }
          .sm-w-full {
            width: 100% !important;
          }
        }
      </style>
      <style>
        @media (max-width: 600px) {
          .sm-dui17-b-t {
            border: solid #4299e1;
            border-width: 4px 0 0;
          }
        }
      </style>
    </head>"""


def create_email(reservation):
    body = f"""
    <body style="box-sizing: border-box; margin: 0; padding: 0; width: 100%; word-break: break-word; -webkit-font-smoothing: antialiased;background-color:#f1f1f1; color:#000000;">
  <table class="wrapper all-font-sans" width="100%" height="100%" cellpadding="0" cellspacing="0" role="presentation">
    <tr>
      <td align="center" style="padding: 24px;" width="100%">
        <table class="sm-w-full" width="650" cellpadding="0" cellspacing="0" role="presentation">
          <tr>
            <td colspan="2" class="sm-inline-block" style="display: none;">
              <img src="https://gile.house{reservation.room.image.url}" width="600" alt="Double Room" style="object-fit: cover;border: 0; line-height: 100%; vertical-align: middle; border-top-left-radius: 4px; border-top-right-radius: 4px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, .1), 0 4px 6px -2px rgba(0, 0, 0, .05);">
            </td>
          </tr>
          <tr>
            <td class="sm-hidden" style="padding-top: 40px; padding-bottom: 40px;" width="160">
              <img src="https://gile.house{reservation.room.image.url}" alt="Room" style="object-fit: cover;border: 0; line-height: 100%; vertical-align: middle; border-top-left-radius: 4px; border-bottom-left-radius: 4px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, .1), 0 4px 6px -2px rgba(0, 0, 0, .05);" width="160" height="350">
            </td>
            <td align="left" class="sm-p-20 sm-dui17-b-t" style="border-radius: 2px; padding: 40px; position: relative; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, .1), 0 4px 6px -2px rgba(0, 0, 0, .05); vertical-align: top; z-index: 50;" bgcolor="#ffffff" valign="top">
              <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
                <tr>
                  <td width="80%">
                    <h1 class="sm-text-lg all-font-roboto" style="font-weight: 700; line-height: 100%; margin: 0; margin-bottom: 4px; font-size: 24px;">Здравей, {reservation.name.split()[0]}!</h1>
                    <p class="sm-text-xs" style="margin: 0; color: #a0aec0; font-size: 14px;">Вашата резервация в къща за гости ГИЛЕ е потвърдена!</p>
                  </td>
                </tr>
              </table>
              <div style="line-height: 32px;">&zwnj;</div>
              <table class="sm-leading-32" style="line-height: 28px; font-size: 14px;" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                <tr>
                  <td class="sm-inline-block"  width="100%">
					<span style="color: #718096; float:left; text-align:left;">Име</span>
					<span style="font-weight: 600; text-align: right;float:right;">{reservation.name.title()}</span>
				  </td>
                </tr>
                <tr>
                  <td class="sm-inline-block" width="100%">
				  <span style="color: #718096; float:left; text-align:left;">Брой нощувки</span>
				  <span style="font-weight: 600; text-align: right;float:right;">{reservation.calc_days}</span>
				  </td>
                </tr>
				<tr>
                   <td class="sm-inline-block" width="100%">
				    <span style="color: #718096; float:left; text-align:left;">Стая</span>
				  <span style="font-weight: 600; text-align: right;float:right;">{reservation.room.room_title}</span>
				  </td>
                </tr>
                <tr>
				   <td class="sm-inline-block" width="100%">
				  <span style="color: #718096; float:left; text-align:left;">Адрес</span>
				  <span style="font-weight: 600; text-align: right;float:right;">Бузлуджа №1, Велико Търново</span>
				  </td>
              </table>
              <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
                <tr>
                  <td style="padding-top: 24px; padding-bottom: 24px;">
                    <div style="background-color: #edf2f7; height: 2px; line-height: 2px;">&zwnj;</div>
                  </td>
                </tr>
              </table>
              <table style="font-size: 14px;" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                <tr>
                  <td class="sm-w-full sm-inline-block sm-text-center" width="100%">
					<span style="float:left; width:40%; text-align:left;">
                    <p class="all-font-roboto" style="margin: 0; margin-bottom: 4px; color: #a0aec0; font-size: 10px; text-transform: uppercase; letter-spacing: 1px;">Настаняване</p>
                    <p class="all-font-roboto" style="font-weight: 600; margin: 0; color: #000000;">{reservation.check_in.date()}</p>
					</span>
					 <span style="font-family: Menlo, Consolas, monospace; font-weight: 600; color: #cbd5e0; font-size: 18px; letter-spacing: -1px; width:2%">&gt;&gt;&gt;</span>
				  <span style="float:right; width:40%; text-align:right">
                    <p class="all-font-roboto" style="margin: 0; margin-bottom: 4px; color: #a0aec0; font-size: 10px; text-transform: uppercase; letter-spacing: 1px;">Напускане</p>
                    <p class="all-font-roboto" style="font-weight: 600; margin: 0; color: #000000;">{reservation.check_out.date()}</p>
					</span>
                  </td>
                </tr>
              </table>
              <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
                <tr>
                  <td style="padding-top: 24px; padding-bottom: 24px;">
                    <div style="background-color: #edf2f7; height: 2px; line-height: 2px;">&zwnj;</div>
                  </td>
                </tr>
              </table>
              <table style="line-height: 28px; font-size: 14px;" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                <tr>
                  <td width="100%">
				  <span style="color: #718096; float:left; text-align:left;">Цена на вечер за {reservation.total_guests} човека</span>
				  <span style="font-weight: 600; text-align: right;float:right;">{reservation.price / reservation.calc_days} лв.</span>
				  </td>
                </tr>
                <tr>
					 <td width="100%">
					 <span style="font-weight: 600; padding-top: 32px; color: #000000; font-size: 20px;float:left; text-align:left;">Общо</span>
					 <span style="font-weight: 600; padding-top: 32px; text-align: right;float:right; color: #68d391; font-size: 20px;">{reservation.price} лв.</span>
					 </td>
                </tr>
              </table>
            <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
        <tr>
          <td style="padding-top: 24px;padding-bottom: 12px;">
            <div style="background-color: #edf2f7; height: 2px; line-height: 2px;">&zwnj;</div>
          </td>
        </tr>
      </table>
      <table style="line-height: 28px; font-size: 14px;" width="100%" cellpadding="0" cellspacing="0" role="presentation">
        <tr>
          <td style="font-weight: bold;" colspan="2">Банкови детайли</td>
        </tr>
        <tr>
            <td width="20%" style="color: #718096;">Име:</td>
            <td>ГИЛЕ ООД</td>
        </tr>
        <tr>
            <td style="color: #718096;">Банка:</td>
            <td>ДСК</td>
        </tr>
        <tr>
            <td style="color: #718096;">BIC:</td>
            <td>STSABGSF</td>
        </tr>
        <tr>
            <td style="color: #718096;">IBAN:</td>
            <td>BG27STSA93001525962185</td>
        </tr>
        <tr>
        
        </tr>
      </table>
      <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
        <tr>
          <td style="padding-top: 24px;padding-bottom: 5px;">
            <div style="background-color: #edf2f7; height: 2px; line-height: 2px;">&zwnj;</div>
          </td>
        </tr>
        <tr>
        <td colspan="2" style="line-height:12px; text-align: center;"><sub style="font-size: 12px;">Това е автоматично генерирано съобщение. Моля, не отговаряйте!</sub></td>
        </tr>
      </table>
            </td>
          </tr>
		  <tr>
            <td class="sm-hidden" style="padding-top: 40px; padding-bottom: 40px;" width="160">
              <img src="https://i.ibb.co/ph7fvky/361616563.jpg" alt="Double room" style="object-fit: cover;border: 0; line-height: 100%; vertical-align: middle; border-top-left-radius: 4px; border-bottom-left-radius: 4px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, .1), 0 4px 6px -2px rgba(0, 0, 0, .05);" width="160" height="350">
            </td>
            <td align="left" class="sm-p-20 sm-dui17-b-t" style="border-radius: 2px; padding: 40px; position: relative; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, .1), 0 4px 6px -2px rgba(0, 0, 0, .05); vertical-align: top; z-index: 50;" bgcolor="#ffffff" valign="top">
              <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
                <tr>
                  <td width="80%">
                    <h1 class="sm-text-lg all-font-roboto" style="font-weight: 700; line-height: 100%; margin: 0; margin-bottom: 4px; font-size: 24px;">Hi, {reservation.name.split()[0]}!</h1>
                    <p class="sm-text-xs" style="margin: 0; color: #a0aec0; font-size: 14px;">Your reservation in guest house GILE is now confirmed!</p>
                  </td>
                </tr>
              </table>
              <div style="line-height: 32px;">&zwnj;</div>
              <table class="sm-leading-32" style="line-height: 28px; font-size: 14px;" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                <tr>
                  <td class="sm-inline-block"  width="100%">
					<span style="color: #718096; float:left; text-align:left;">Guest</span>
					<span style="font-weight: 600; text-align: right;float:right;">{reservation.name}</span>
				  </td>
                </tr>
                <tr>
                  <td class="sm-inline-block" width="100%">
				  <span style="color: #718096; float:left; text-align:left;">Nights</span>
				  <span style="font-weight: 600; text-align: right;float:right;">{reservation.calc_days}</span>
				  </td>
                </tr>
				<tr>
                   <td class="sm-inline-block" width="100%">
				    <span style="color: #718096; float:left; text-align:left;">Room</span>
				  <span style="font-weight: 600; text-align: right;float:right;">{reservation.room.room_title_en}</span>
				  </td>
                </tr>
                <tr>
				   <td class="sm-inline-block" width="100%">
				  <span style="color: #718096; float:left; text-align:left;">Address</span>
				  <span style="font-weight: 600; text-align: right;float:right;">Buzludzha" №1 str., Veliko Tarnovo, Bulgaria</span>
				  </td>
              </table>
              <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
                <tr>
                  <td style="padding-top: 24px; padding-bottom: 24px;">
                    <div style="background-color: #edf2f7; height: 2px; line-height: 2px;">&zwnj;</div>
                  </td>
                </tr>
              </table>
              <table style="font-size: 14px;" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                <tr>
                  <td class="sm-w-full sm-inline-block sm-text-center" width="100%">
					<span style="float:left; width:40%; text-align:left;">
                    <p class="all-font-roboto" style="margin: 0; margin-bottom: 4px; color: #a0aec0; font-size: 10px; text-transform: uppercase; letter-spacing: 1px;">Check-in</p>
                    <p class="all-font-roboto" style="font-weight: 600; margin: 0; color: #000000;">{reservation.check_in.date()}</p>
					</span>
					 <span style="font-family: Menlo, Consolas, monospace; font-weight: 600; color: #cbd5e0; font-size: 18px; letter-spacing: -1px; width:2%">&gt;&gt;&gt;</span>
				  <span style="float:right; width:40%; text-align:right">
                    <p class="all-font-roboto" style="margin: 0; margin-bottom: 4px; color: #a0aec0; font-size: 10px; text-transform: uppercase; letter-spacing: 1px;">Check-out</p>
                    <p class="all-font-roboto" style="font-weight: 600; margin: 0; color: #000000;">{reservation.check_out}</p>
					</span>
                  </td>
                </tr>
              </table>
              <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
                <tr>
                  <td style="padding-top: 24px; padding-bottom: 24px;">
                    <div style="background-color: #edf2f7; height: 2px; line-height: 2px;">&zwnj;</div>
                  </td>
                </tr>
              </table>
              <table style="line-height: 28px; font-size: 14px;" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                <tr>
                  <td width="100%">
				  <span style="color: #718096; float:left; text-align:left;">Price per night for {reservation.total_guests} guests</span>
				  <span style="font-weight: 600; text-align: right;float:right;">{reservation.price / reservation.calc_days} BGN</span>
				  </td>
                </tr>
                <tr>
					 <td width="100%">
					 <span style="font-weight: 600; padding-top: 32px; color: #000000; font-size: 20px;float:left; text-align:left;">Total</span>
					 <span style="font-weight: 600; padding-top: 32px; text-align: right;float:right; color: #68d391; font-size: 20px;">{reservation.price} BGN</span>
					 </td>
                </tr>
              </table>
                      <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
        <tr>
          <td style="padding-top: 24px;padding-bottom: 12px;">
            <div style="background-color: #edf2f7; height: 2px; line-height: 2px;">&zwnj;</div>
          </td>
        </tr>
      </table>
      <table style="line-height: 28px; font-size: 14px;" width="100%" cellpadding="0" cellspacing="0" role="presentation">
        <tr>
          <td style="font-weight: bold;" colspan="2">Bank Details</td>
        </tr>
        <tr>
            <td width="20%" style="color: #718096;">Name:</td>
            <td>GILE OOD</td>
        </tr>
        <tr>
            <td style="color: #718096;">Bank:</td>
            <td>DSK BANK EAD</td>
        </tr>
        <tr>
            <td style="color: #718096;">BIC:</td>
            <td>STSABGSF</td>
        </tr>
        <tr>
            <td style="color: #718096;">IBAN:</td>
            <td>BG27STSA93001525962185</td>
        </tr>
      </table>
      <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
        <tr>
          <td style="padding-top: 24px;padding-bottom: 5px;">
            <div style="background-color: #edf2f7; height: 2px; line-height: 2px;">&zwnj;</div>
          </td>
        </tr>
        <tr>
        <td colspan="2" style="line-height:12px; text-align: center;"><sub style="font-size: 12px;">This is an automated notification email, please do not reply.</sub></td>
        </tr>
      </table>
              </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
    """
    return HEAD + body
