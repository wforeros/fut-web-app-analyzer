import random
from time import sleep
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from options import get_target_filter
from src.modules.market.transfer_market import define_filters
from src.scraper.selenium_setup import load_driver
import time



class WebApp(): 
  def __init__(self):
    self.driver = load_driver()
    # self.driver.get("https://www.ea.com/es-es/ea-sports-fc/ultimate-team/web-app/")
    self.user_requests_made = 0
    self.filter = {}

  def go_to_transfer_market(self, search_players = False, filters = None):
    """
    Clicks Transfer Market button on sidebar.

    Location:
        anywhere
    """
    try:
      self.__bid_status_bug = False
      self.__go_to_transfers_section()
      self.sleep_approx(2)
      self.driver.find_element(
        By.CLASS_NAME, 'ut-tile-transfer-market').click()
      if not filters: 
        self.filter = define_filters()
      else:
        self.filter = filters.copy()

      if search_players:
        self.search_players()
    except Exception as e:
      print("Exception retrying go_transfer_market", e)

  def search_players(self):
    """
    Searches for players in transfer market.
    It is needed to be in the search transfer market page where form is located.

    Location:
        Transfer Market
    """
    try:
      self.pages_amount = 0
      self.sleep_approx(2)
      WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located(
          (By.CLASS_NAME, 'ut-text-input-control'))
      )

      self.__set_quality_and_rarity()
      self.sleep_approx(1)

      minPriceField = '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[2]/div[2]/div[2]/input'
      maxPriceField = '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[2]/div[3]/div[2]/input'
      minBuyNowField = '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[2]/div[5]/div[2]/input'
      
      min_price_element = self.driver.find_element(
        By.XPATH, minPriceField)
      min_price_element.clear()
      min_price_element.send_keys(self.filter.get('min_price'))
      self.sleep_approx(1.5)

      max_price_element = self.driver.find_element(By.XPATH, maxPriceField)
      max_price_element.clear()
      max_price_element.send_keys(self.filter.get('max_price'))
      self.sleep_approx(1.5)

      min_buy_now_element = self.driver.find_element(By.XPATH, minBuyNowField)
      min_buy_now_element.clear()
      min_buy_now_element.send_keys(self.filter.get('min_buy_now')) 
      self.sleep_approx(2)

      # Click en boton search
      self.driver.find_element(
          By.XPATH, '(//*[@class="button-container"]/button)[2]').click()
      # for i in range(1, 5):
      #   self.sleep_approx(1)
      #   self.__go_to_next_page()
      #   WebDriverWait(self.driver, 10).until(
      #   EC.visibility_of_element_located(
      #     (By.CLASS_NAME, 'SearchResults'))
      #   )
      self.user_requests_made += 1
      for i in range(1, int(self.filter.get('pages'))):
        self.filter_players()
        self.sleep_approx(1)
        self.__go_to_next_page()
    except Exception as e:
      print("Exception retrying search_players", e)

  def filter_players(self):
    self.sleep_approx(1)
    paginated_item_list = self.driver.find_element(By.CLASS_NAME, 'paginated-item-list')
    list_items = paginated_item_list.find_elements(By.XPATH, '//li[contains(@class, "listFUTItem")]')
    for player_item in list_items:
      try:
        entity_container = player_item.find_element(By.CLASS_NAME, 'entityContainer')
        player_rating = int(entity_container.find_element(By.CLASS_NAME, 'rating').text)
        bid_label = player_item.find_element(By.XPATH, './/*[contains(text(), "Bid")]')
        current_bid = bid_label.find_element(By.XPATH, './following-sibling::span').text
        current_bid = int(current_bid.replace(',', '')) if '-' not in current_bid else 0
        if player_rating >= int(self.filter.get('player_rating')) and current_bid <= int(self.filter.get('max_price')):
          entity_container.click()
          print("El jugador cumple con los requisitos")
          print("Calificacion del jugador:", player_rating)
          print("Valor de puja actual:", current_bid)
          self.__bid_player()
          
      except Exception as e:
        print('Error leyendo a un jugador. Puede que ya haya sido vendido.', e)
      self.sleep_approx(1.2)

  def go_to_targets(self, filters = None):
    self.__bid_status_bug = False
    self.__go_to_transfers_section()
    self.driver.find_element(By.CLASS_NAME, 'ut-tile-transfer-targets').click()
    
    if not filters:
      self.targets_filter = get_target_filter()
      print("No se ha definido un filtro de jugadores. Se utilizará el filtro de option.py.")
    else: 
      self.targets_filter = filters

    WebDriverWait(self.driver, 10).until(
      EC.visibility_of_element_located(
        (By.CLASS_NAME, 'sectioned-item-list')
      )
    )
    # outbids_list = active_bids_section.find_elements(By.XPATH, '//li[contains(@class, "outbid")]')
    while True:
      active_bids_section = self.driver.find_element(By.XPATH, '/html/body/main/section/section/div[2]/div/div/div/section[1]')
      active_bids = active_bids_section.find_elements(By.CLASS_NAME, 'listFUTItem')
      if len(active_bids) == 0:
        print('No hay pujas que superar. Fin del monitoreo.')
        break
      for bid in active_bids:
        try:
          if bid.find_element(By.CLASS_NAME, 'outbid'):
            print('Analizando puja superada')
            bid.click()
            self.sleep_approx(3)
            # Esperar a que la descripci'on del jugador se cargue
            WebDriverWait(self.driver, 10).until(
              EC.visibility_of_element_located(
                (By.CLASS_NAME, 'currentBid'))
            )
            WebDriverWait(self.driver, 10).until(
              EC.visibility_of_element_located(
                (By.CLASS_NAME, 'rating'))
            )
            current_bid = self.driver.find_element(By.CLASS_NAME, 'currentBid').find_element(By.CLASS_NAME, 'currency-coins').text.replace(',', '')
            current_bid = int(current_bid)
            player_view = bid.find_element(By.CLASS_NAME, 'entityContainer')#.find_element(By.CLASS_NAME, 'rating').text
            name = bid.find_element(By.CLASS_NAME, 'name.watchIcon').text
            rating = player_view.find_element(By.CLASS_NAME, 'rating').text
            
            self.sleep_approx(1)
            # is_expiring = len(player_view.find_elements(By.CLASS_NAME, 'expiring')) > 0
            print("Hay una puja que ha sido superada", name, rating, current_bid)
            # if is_expiring:
            is_outbid = len(player_view.find_elements(By.CLASS_NAME, 'outbid')) > 0
            # if is_outbid
            if current_bid <= int(self.targets_filter.get('max_price')) and is_outbid and int(rating) >= int(self.targets_filter.get('player_rating')):
              print("Pujando de nuevo.")
              self.__bid_player()
            else:
              print("La puja actual es mayor al precio máximo establecido. La puja actual es de:", current_bid, "por ", name, " con media de:", rating)
              # Click unwatch porque ya no se debe pujar
              self.driver.find_element(By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[1]/div/div[3]/button').click()
              # Esperar a que aparezca mensaje de confirmación
              WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                  (By.CLASS_NAME, 'Notification.neutral'))
              )
        except Exception as e:
          # print('Error leyendo a un jugador. Puede que ya haya sido vendido.')
          continue
        self.sleep_approx(1)
        
      self.sleep_approx(15)



  def __set_quality_and_rarity(self):
    """
    Sets quality and rarity to gold.
    """
    
    # Quality button
    self.driver.find_element(By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[2]/div').click()
    self.sleep_approx(1)
    WebDriverWait(self.driver, 10).until(
      EC.visibility_of_element_located(
        (By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[2]/div')
      )
    )
    self.driver.find_element(By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[2]/div/ul/li[4]').click()
    self.sleep_approx(2)

    # Rarity button
    self.driver.find_element(By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[3]/div/div').click()
    self.sleep_approx(1)
    WebDriverWait(self.driver, 10).until(
      EC.visibility_of_element_located(
        (By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[3]/div')
      )
    )
    self.driver.find_element(By.XPATH, '//li[contains(text(), "Rare")]').click()

  def __bid_player(self):
    if self.__bid_status_bug: 
      print('No ha sido posible pujar por el jugador. Se ha detectado el bug de estado de puja en otro jugador. Para prevenir baneos no se seguirá pujando.')
      return
    WebDriverWait(self.driver, 10).until(
      EC.visibility_of_element_located(
        (By.CLASS_NAME, 'bidButton'))
    )
    self.driver.find_element(By.CLASS_NAME, 'bidButton').click()
    self.sleep_approx(2)
    WebDriverWait(self.driver, 2).until(
      EC.visibility_of_element_located(
        (By.CLASS_NAME, 'negative'))
    )
    self.__check_higher_bid()
    
    is_negative_notification = len(self.driver.find_elements(By.CLASS_NAME, 'Notification.negative')) > 0
    if is_negative_notification:
      self.__open_player_bio()
      self.__bid_player()
      self.__bid_status_bug = True
      Exception("No se pudo realizar la puja. El jugador ya fue vendido o no se actualizó correctamente.")
      
    else:
      print("Puja realizada con éxito.")
    self.sleep_approx(1)

  def __check_higher_bid(self):
    try:
      dialog_msg = self.driver.find_element(By.CLASS_NAME, 'ea-dialog-view--body')
      if dialog_msg:
        cancel_button = dialog_msg.find_element(By.CLASS_NAME, "negative")
        if cancel_button:
          cancel_button.click()
          self.sleep_approx(2)
          return True
    except Exception as e:
      pass
    return False
  
  def __open_player_bio(self):
    detail_panel = self.driver.find_element(By.CLASS_NAME, 'DetailPanel')
    detail_panel.find_element(By.CLASS_NAME, 'more').click()
    WebDriverWait(self.driver, 10).until( 
      EC.visibility_of_element_located(
        (By.CLASS_NAME, 'ui-layout-right'))
    )

    self.sleep_approx(1.2)
    right_layout = self.driver.find_element(By.CLASS_NAME, 'ui-layout-right')
    right_layout.find_element(By.CLASS_NAME, 'ut-navigation-button-control').click()

    
  def __go_to_transfers_section(self):
    self.driver.find_element(By.CLASS_NAME, 'icon-transfer').click()
    sleeptime = random.randint(1, 5)
    # selling = str(self.getText(
    #   "/html/body/main/section/section/div[2]/div/div/div[3]/div[2]/div/div[2]/span[2]"))
    # self.user_transferlist_selling = selling

    self.sleep_approx(sleeptime)
    WebDriverWait(self.driver, 10).until(
      EC.visibility_of_element_located(
        (By.CLASS_NAME, 'ut-tile-transfer-market'))
    )

  def __go_to_next_page(self):
    """
    Goes to next page in transfer market.

    Location:
        Transfer Market
    """
    print("Cambiando de página")
    WebDriverWait(self.driver, 10).until(
      EC.visibility_of_element_located(
        (By.CLASS_NAME, 'pagination.next'))
    )
    self.driver.find_element(By.CLASS_NAME, 'pagination.next').click()
    self.sleep_approx(2)

  def sleep_approx(self, seconds):
    """
    Randomizes sleep to avoid detection.
    """
    upperbound = (seconds+0.2)*10000
    if (seconds >= 1):
        lowerbound = (seconds-0.2)*10000
    else:
        lowerbound = seconds*10000

    lowerbound = int(lowerbound)
    upperbound = int(upperbound)

    sleeptime = random.randint(lowerbound, upperbound)
    sleeptime = sleeptime/10000
    sleeptime = sleeptime*.8

    print("Sleeping for", sleeptime, "seconds")
    sleep(sleeptime)