def define_filters():
  min_price = input("Precio mínimo: ")
  max_price = input("Precio máximo: ")
  min_buy_now = input("Precio mínimo de compra ya: ")
  player_rating = input("Rating de los jugadores: ")
  pages_amount = input("Cantidad de páginas a buscar: ")
  return {
    "min_price": min_price,
    "max_price": max_price,
    "min_buy_now": min_buy_now,
    "player_rating": player_rating,
    "pages": pages_amount
  }