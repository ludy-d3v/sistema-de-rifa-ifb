import React, { useEffect, useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'
import {
  ArrowRight,
  CalendarDays,
  Check,
  CheckCircle2,
  Clock3,
  CreditCard,
  Gift,
  Menu,
  Moon,
  Search,
  ShoppingCart,
  Shuffle,
  Sun,
  Ticket,
  Trophy,
  Users,
  X
} from 'lucide-react'
import './styles.css'

const money = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL'
})

const statusLabels = {
  disponivel: 'Disponível',
  reservado: 'Reservado',
  aguardando_aprovacao: 'Aguardando aprovação',
  pago: 'Pago'
}

const numberFilters = [
  { value: 'todos', label: 'Todos' },
  { value: 'disponivel', label: 'Disponíveis' },
  { value: 'reservado', label: 'Reservados' },
  { value: 'aguardando_aprovacao', label: 'Aguardando' },
  { value: 'pago', label: 'Pagos' }
]

function getSlugFromPath() {
  const match = window.location.pathname.match(/^\/rifa\/([^/]+)/)
  return match?.[1] || null
}

function getInitialTheme() {
  const savedTheme = localStorage.getItem('rifafacil-theme')
  if (savedTheme === 'light' || savedTheme === 'dark') return savedTheme
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: options.body instanceof FormData ? undefined : { 'Content-Type': 'application/json' },
    ...options
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    const message = typeof data === 'string' ? data : JSON.stringify(data)
    throw new Error(message || 'Não foi possível concluir a operação.')
  }
  return data
}

function App() {
  const [slug, setSlug] = useState(getSlugFromPath())
  const [theme, setTheme] = useState(getInitialTheme)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    document.documentElement.dataset.theme = theme
    localStorage.setItem('rifafacil-theme', theme)
  }, [theme])

  function abrirRifa(novoSlug) {
    window.history.pushState({}, '', `/rifa/${novoSlug}`)
    setSlug(novoSlug)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function voltarInicio() {
    window.history.pushState({}, '', '/')
    setSlug(null)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function alternarTema() {
    setTheme((current) => (current === 'dark' ? 'light' : 'dark'))
  }

  useEffect(() => {
    const onPopState = () => setSlug(getSlugFromPath())
    window.addEventListener('popstate', onPopState)
    return () => window.removeEventListener('popstate', onPopState)
  }, [])

  return slug ? (
    <PaginaRifa slug={slug} voltarInicio={voltarInicio} theme={theme} alternarTema={alternarTema} />
  ) : (
    <Home abrirRifa={abrirRifa} theme={theme} alternarTema={alternarTema} />
  )
}

function Header({ voltarInicio, theme, alternarTema }) {
  const [menuAberto, setMenuAberto] = useState(false)
  const isDark = theme === 'dark'

  function navegarInicio() {
    setMenuAberto(false)
    if (voltarInicio) {
      voltarInicio()
      return
    }
    window.history.pushState({}, '', '/')
    window.dispatchEvent(new PopStateEvent('popstate'))
  }

  return (
    <header className="topbar">
      <div className="topbarInner">
        <button className="brand" onClick={navegarInicio} aria-label="Ir para o início">
          <img src="/logo-rifafacil-icon.png" alt="" />
          <span>Rifa Fácil</span>
        </button>

        <nav className={`navLinks ${menuAberto ? 'open' : ''}`} aria-label="Navegação principal">
          <button onClick={navegarInicio}>Início</button>
          <a href="/#rifas" onClick={() => setMenuAberto(false)}>Rifas</a>
          <a href="/#como-funciona" onClick={() => setMenuAberto(false)}>Como funciona</a>
        </nav>

        <div className="topbarActions">
          <button
            className="themeToggle"
            onClick={alternarTema}
            title="Alternar tema"
            aria-label="Alternar tema"
          >
            {isDark ? <Moon size={19} /> : <Sun size={19} />}
          </button>
          <button
            className="menuButton"
            onClick={() => setMenuAberto((current) => !current)}
            aria-label={menuAberto ? 'Fechar menu' : 'Abrir menu'}
          >
            {menuAberto ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>
    </header>
  )
}

function Home({ abrirRifa, theme, alternarTema }) {
  const [rifas, setRifas] = useState([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState('')

  useEffect(() => {
    requestJson('/api/rifas-publicas/')
      .then(setRifas)
      .catch(() => setErro('Não foi possível carregar as rifas disponíveis.'))
      .finally(() => setCarregando(false))
  }, [])

  const totalNumeros = rifas.reduce((total, rifa) => total + Number(rifa.total_numeros || 0), 0)

  return (
    <>
      <Header theme={theme} alternarTema={alternarTema} />
      <main className="home">
        <section className="hero">
          <div className="heroContent">
            <Badge icon={Ticket}>Campanha ativa</Badge>
            <h1>
              Participe de rifas digitais <span>com segurança.</span>
            </h1>
            <p>
              Encontre campanhas ativas, selecione seus números e envie o comprovante de forma
              simples, segura e organizada.
            </p>
            <div className="heroActions">
              <a className="primary cta" href="#rifas">
                Ver rifas disponíveis <ArrowRight size={18} />
              </a>
              <a className="secondaryButton" href="#como-funciona">
                Como funciona
              </a>
            </div>
            <div className="trustRow">
              <TrustItem icon={CheckCircle2} label="Processo simples" />
              <TrustItem icon={Clock3} label="Reserva rápida" />
              <TrustItem icon={CreditCard} label="Pagamento seguro" />
            </div>
            <div className="heroStats">
              <strong>{rifas.length || 2}<span>rifas ativas</span></strong>
              <strong>{totalNumeros || 180}+<span>números disponíveis</span></strong>
              <strong>100%<span>fluxo auditável</span></strong>
            </div>
          </div>

          <div className="heroMockup" aria-label="Prévia visual de uma rifa">
            <img className="phoneArtwork" src="/hero-phone.png" alt="" />
          </div>
        </section>

        <section className="section" id="rifas">
          <div className="sectionHeader">
            <div>
              <span className="sectionKicker">Campanhas abertas</span>
              <h2>Rifas disponíveis</h2>
            </div>
            <span>{rifas.length} campanha(s)</span>
          </div>

          {carregando && <RaffleSkeleton />}
          {erro && <Alert tone="error">{erro}</Alert>}

          <div className="rifaGrid">
            {rifas.map((rifa) => (
              <RaffleCard rifa={rifa} abrirRifa={abrirRifa} key={rifa.id} />
            ))}
          </div>

          {!carregando && !erro && rifas.length === 0 && (
            <EmptyState icon={Ticket} title="Nenhuma rifa ativa" text="Quando uma campanha estiver ativa, ela aparecerá aqui." />
          )}
        </section>

        <section className="section flowSection" id="como-funciona">
          <div>
            <span className="sectionKicker">Compra simples</span>
            <h2>Do número escolhido ao comprovante enviado.</h2>
          </div>
          <div className="flowGrid">
            <InfoCard icon={Search} title="Escolha a campanha" text="Veja prêmios, data do sorteio, progresso e vendedores vinculados." />
            <InfoCard icon={Ticket} title="Reserve seus números" text="Selecione individualmente na grade e informe seus dados com CPF." />
            <InfoCard icon={CreditCard} title="Envie o comprovante" text="Anexe PNG, JPG ou PDF para o organizador validar o pagamento." />
          </div>
        </section>
      </main>
    </>
  )
}

function PaginaRifa({ slug, voltarInicio, theme, alternarTema }) {
  const [rifa, setRifa] = useState(null)
  const [selecionados, setSelecionados] = useState([])
  const [form, setForm] = useState({
    comprador_nome: '',
    comprador_email: '',
    comprador_telefone: '',
    comprador_cpf: '',
    vendedor: ''
  })
  const [transacao, setTransacao] = useState(null)
  const [comprovante, setComprovante] = useState(null)
  const [mensagem, setMensagem] = useState('')
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(true)
  const [reservando, setReservando] = useState(false)
  const [enviandoComprovante, setEnviandoComprovante] = useState(false)
  const [buscaNumero, setBuscaNumero] = useState('')
  const [filtroStatus, setFiltroStatus] = useState('todos')

  useEffect(() => {
    setCarregando(true)
    requestJson(`/api/rifa/${slug}/public/`)
      .then((data) => {
        setRifa(data)
        setSelecionados([])
        setTransacao(null)
        setMensagem('')
        setErro('')
        setForm((atual) => ({
          ...atual,
          vendedor: data.vendedores?.[0]?.id ? String(data.vendedores[0].id) : ''
        }))
      })
      .catch(() => setErro('Rifa não encontrada ou indisponível.'))
      .finally(() => setCarregando(false))
  }, [slug])

  const total = useMemo(() => {
    if (!rifa) return 0
    return selecionados.length * Number(rifa.valor_numero)
  }, [rifa, selecionados])

  const numerosVisiveis = useMemo(() => {
    if (!rifa) return []
    return rifa.numeros.filter((numero) => {
      const combinaBusca = buscaNumero ? String(numero.numero).includes(buscaNumero.trim()) : true
      const combinaStatus = filtroStatus === 'todos' ? true : numero.status === filtroStatus
      return combinaBusca && combinaStatus
    })
  }, [rifa, buscaNumero, filtroStatus])

  function alternarNumero(numero) {
    if (transacao && transacao.status !== 'reservada') {
      setTransacao(null)
      setMensagem('')
      setErro('')
    }
    setSelecionados((atuais) =>
      atuais.includes(numero) ? atuais.filter((item) => item !== numero) : [...atuais, numero]
    )
  }

  function atualizarCampo(event) {
    const { name, value } = event.target
    setForm((atual) => ({ ...atual, [name]: value }))
  }

  function selecionarAleatorios() {
    if (!rifa) return
    const disponiveis = rifa.numeros
      .filter((numero) => numero.status === 'disponivel' && !selecionados.includes(numero.numero))
      .map((numero) => numero.numero)
    const sorteados = disponiveis.sort(() => Math.random() - 0.5).slice(0, 5)
    setSelecionados((atuais) => [...atuais, ...sorteados])
  }

  async function reservar(event) {
    event.preventDefault()
    setErro('')
    setMensagem('')
    setReservando(true)
    try {
      const payload = {
        numeros: selecionados,
        comprador_nome: form.comprador_nome,
        comprador_email: form.comprador_email,
        comprador_telefone: form.comprador_telefone,
        comprador_cpf: form.comprador_cpf
      }
      if (form.vendedor) payload.vendedor = form.vendedor
      const data = await requestJson(`/api/rifa/${rifa.slug}/reservar/`, {
        method: 'POST',
        body: JSON.stringify(payload)
      })
      setTransacao(data)
      setComprovante(null)
      setSelecionados([])
      setMensagem('Reserva criada. Envie o comprovante para o organizador avaliar o pagamento.')
      const refreshed = await requestJson(`/api/rifa/${rifa.slug}/public/`)
      setRifa(refreshed)
    } catch (error) {
      setErro('Não foi possível criar a reserva. Verifique os números e os dados informados.')
    } finally {
      setReservando(false)
    }
  }

  async function enviarComprovante(event) {
    event.preventDefault()
    if (!comprovante || !transacao) return
    setErro('')
    setMensagem('')
    setEnviandoComprovante(true)
    try {
      const body = new FormData()
      body.append('comprovante', comprovante)
      const data = await requestJson(`/api/transacoes/${transacao.id}/comprovante/`, {
        method: 'POST',
        body
      })
      setTransacao((atual) => ({ ...atual, ...data, status: 'aguardando_aprovacao' }))
      setComprovante(null)
      setForm((atual) => ({
        ...atual,
        comprador_nome: '',
        comprador_email: '',
        comprador_telefone: '',
        comprador_cpf: ''
      }))
      setMensagem('Comprovante enviado. Sua reserva está aguardando aprovação.')
      const refreshed = await requestJson(`/api/rifa/${rifa.slug}/public/`)
      setRifa(refreshed)
    } catch (error) {
      setErro('Não foi possível enviar o comprovante. Use PNG, JPG ou PDF com até 5MB.')
    } finally {
      setEnviandoComprovante(false)
    }
  }

  if (carregando) {
    return (
      <>
        <Header voltarInicio={voltarInicio} theme={theme} alternarTema={alternarTema} />
        <main className="page"><DetailSkeleton /></main>
      </>
    )
  }

  if (!rifa) {
    return (
      <>
        <Header voltarInicio={voltarInicio} theme={theme} alternarTema={alternarTema} />
        <main className="page"><Alert tone="error">{erro}</Alert></main>
      </>
    )
  }

  return (
    <>
      <Header voltarInicio={voltarInicio} theme={theme} alternarTema={alternarTema} />
      <main className="page">
        <section className="raffleHeader">
          <div className="raffleIntro">
            <button className="backButton" onClick={voltarInicio}>Início</button>
            <Badge icon={Ticket}>Rifa ativa</Badge>
            <h1>{rifa.titulo}</h1>
            <p>{rifa.descricao}</p>
            <div className="metricGrid">
              <Metric icon={CreditCard} label="Valor do número" value={money.format(Number(rifa.valor_numero))} />
              <Metric icon={CalendarDays} label="Data do sorteio" value={new Date(rifa.data_sorteio).toLocaleDateString('pt-BR')} />
              <Metric icon={Users} label="Números pagos" value={`${rifa.numeros_pagos}/${rifa.total_numeros}`} />
            </div>
            <div className="progressBlock">
              <div>
                <span>Progresso da campanha</span>
                <strong>{rifa.percentual_vendido}%</strong>
              </div>
              <Progress value={rifa.percentual_vendido} />
            </div>
          </div>

          <div className="raffleMedia">
            {rifa.imagem_principal_url ? (
              <img src={rifa.imagem_principal_url} alt="" />
            ) : (
              <EmptyVisual icon={Trophy} />
            )}
          </div>
        </section>

        {mensagem && <Alert tone="success">{mensagem}</Alert>}
        {erro && <Alert tone="error">{erro}</Alert>}

        <div className="shopLayout">
          <div className="contentStack">
            <section className="panel">
              <div className="sectionHeader">
                <div>
                  <span className="sectionKicker">Prêmios</span>
                  <h2>Destaques da rifa</h2>
                </div>
              </div>
              <div className="premios">
                {rifa.premios.length ? rifa.premios.map((premio, index) => (
                  <PrizeCard premio={premio} destaque={index === 0} key={premio.id} />
                )) : <EmptyState icon={Gift} title="Nenhum prêmio cadastrado" text="Os prêmios aparecerão aqui assim que forem cadastrados." />}
              </div>
            </section>

            <section className="panel">
              <div className="sectionHeader numbersHeader">
                <div>
                  <span className="sectionKicker">Seleção</span>
                  <h2>Grade de números</h2>
                </div>
                <Legend />
              </div>

              <div className="numberToolbar">
                <label className="searchField">
                  <Search size={18} />
                  <input
                    value={buscaNumero}
                    onChange={(event) => setBuscaNumero(event.target.value.replace(/\D/g, ''))}
                    placeholder="Buscar número"
                    inputMode="numeric"
                  />
                </label>
                <select value={filtroStatus} onChange={(event) => setFiltroStatus(event.target.value)} aria-label="Filtrar números por status">
                  {numberFilters.map((filter) => (
                    <option value={filter.value} key={filter.value}>{filter.label}</option>
                  ))}
                </select>
                <button className="secondaryButton compact" onClick={selecionarAleatorios} type="button">
                  <Shuffle size={17} /> Selecionar aleatórios
                </button>
                <button className="ghostLight compact" onClick={() => setSelecionados([])} type="button" disabled={!selecionados.length}>
                  Limpar seleção
                </button>
              </div>

              <div className="numbersGrid">
                {numerosVisiveis.map((numero) => (
                  <NumberButton
                    numero={numero}
                    selected={selecionados.includes(numero.numero)}
                    onClick={() => alternarNumero(numero.numero)}
                    key={numero.id}
                  />
                ))}
              </div>
            </section>
          </div>

          <aside className="checkout">
            <div className="checkoutTitle">
              <ShoppingCart size={22} />
              <h2>Carrinho</h2>
            </div>

            {!transacao && (
              <>
                <div className="selectedChips">
                  {selecionados.length ? selecionados.slice().sort((a, b) => a - b).map((numero) => (
                    <button type="button" onClick={() => alternarNumero(numero)} key={numero}>#{numero}</button>
                  )) : <span>Nenhum número selecionado</span>}
                </div>

                <div className="summaryBox">
                  <span>{selecionados.length} número(s)</span>
                  <strong>{money.format(total)}</strong>
                </div>

                <form onSubmit={reservar} className="form">
                  <h3>Dados do participante</h3>
                  <label>Nome completo<input name="comprador_nome" value={form.comprador_nome} onChange={atualizarCampo} required /></label>
                  <label>E-mail<input name="comprador_email" type="email" value={form.comprador_email} onChange={atualizarCampo} required /></label>
                  <label>Telefone<input name="comprador_telefone" value={form.comprador_telefone} onChange={atualizarCampo} required /></label>
                  <label>CPF<input name="comprador_cpf" value={form.comprador_cpf} onChange={atualizarCampo} required /></label>
                  {rifa.vendedores.length > 0 && (
                    <label>
                      Vendedor
                      <select name="vendedor" value={form.vendedor} onChange={atualizarCampo} required>
                        {rifa.vendedores.map((vendedor) => (
                          <option key={vendedor.id} value={vendedor.id}>{vendedor.nome}</option>
                        ))}
                      </select>
                    </label>
                  )}
                  <button className="primary full" disabled={!selecionados.length || reservando}>
                    {reservando ? 'Reservando...' : <>Reservar números <CheckCircle2 size={18} /></>}
                  </button>
                </form>
              </>
            )}

            {transacao?.status === 'reservada' && (
              <form onSubmit={enviarComprovante} className="form upload">
                <div className="paymentHeader">
                  <CreditCard size={20} />
                  <div>
                    <h3>Pagamento</h3>
                    <span className="paymentStatus">{statusLabels[transacao.status] || transacao.status}</span>
                  </div>
                </div>

                <div className="pixBox">
                  <span>Chave Pix</span>
                  <strong>{rifa.chave_pix || 'Chave Pix não cadastrada'}</strong>
                </div>

                <label className="fileDrop">
                  <input type="file" accept="image/png,image/jpeg,application/pdf" onChange={(event) => setComprovante(event.target.files[0])} required />
                  <span>Comprovante</span>
                  <strong>{comprovante ? comprovante.name : 'Clique para anexar PNG, JPG ou PDF'}</strong>
                </label>

                <button className="primary full" disabled={enviandoComprovante}>
                  {enviandoComprovante ? 'Enviando...' : <>Enviar comprovante <ArrowRight size={18} /></>}
                </button>
              </form>
            )}

            {transacao && transacao.status !== 'reservada' && (
              <div className="paymentClosed">
                <CheckCircle2 size={20} />
                <div>
                  <strong>Pagamento em análise</strong>
                  <span>Status atual: {statusLabels[transacao.status] || transacao.status}</span>
                  <small>Para fazer outra reserva, selecione novos números na grade.</small>
                </div>
              </div>
            )}
          </aside>
        </div>
      </main>
    </>
  )
}

function RaffleCard({ rifa, abrirRifa }) {
  return (
    <article className="rifaCard">
      <div className="rifaImageWrap">
        {rifa.imagem_principal_url ? (
          <img src={rifa.imagem_principal_url} alt="" className="rifaImage" />
        ) : (
          <div className="rifaImage placeholder">
            <Ticket size={42} />
          </div>
        )}
        <span className="statusBadge">{rifa.status}</span>
      </div>
      <div className="rifaContent">
        <h3>{rifa.titulo}</h3>
        <p>{rifa.descricao || 'Rifa disponível para reserva de números.'}</p>
        <div className="cardMeta">
          <span><CalendarDays size={16} /> {new Date(rifa.data_sorteio).toLocaleDateString('pt-BR')}</span>
          <span><Users size={16} /> {rifa.numeros_pagos}/{rifa.total_numeros} pagos</span>
        </div>
        <div className="cardProgress">
          <Progress value={rifa.percentual_vendido} />
          <strong>{rifa.percentual_vendido}%</strong>
        </div>
      </div>
      <div className="cardFooter">
        <div>
          <span>Valor</span>
          <strong>{money.format(Number(rifa.valor_numero))}</strong>
        </div>
        <button className="primary" onClick={() => abrirRifa(rifa.slug)}>
          Ver rifa <ArrowRight size={17} />
        </button>
      </div>
    </article>
  )
}

function PrizeCard({ premio, destaque }) {
  return (
    <article className={`premio ${destaque ? 'featured' : ''}`}>
      {premio.imagem_url ? <img src={premio.imagem_url} alt="" /> : <EmptyVisual icon={Gift} />}
      <div>
        <span>{premio.posicao}º prêmio</span>
        <strong>{premio.descricao}</strong>
      </div>
    </article>
  )
}

function NumberButton({ numero, selected, onClick }) {
  const available = numero.status === 'disponivel'
  return (
    <button
      className={`number ${numero.status} ${selected ? 'selected' : ''}`}
      disabled={!available}
      onClick={onClick}
      title={statusLabels[numero.status]}
      aria-label={`Número ${numero.numero}, ${statusLabels[numero.status]}`}
    >
      {selected && <Check size={13} />}
      <span>{numero.numero}</span>
    </button>
  )
}

function Badge({ icon: Icon, children }) {
  return (
    <span className="badge">
      <Icon size={15} />
      {children}
    </span>
  )
}

function TrustItem({ icon: Icon, label }) {
  return (
    <span className="trustItem">
      <Icon size={18} />
      {label}
    </span>
  )
}

function InfoCard({ icon: Icon, title, text }) {
  return (
    <article className="infoCard">
      <span><Icon size={22} /></span>
      <strong>{title}</strong>
      <p>{text}</p>
    </article>
  )
}

function Metric({ icon: Icon, label, value }) {
  return (
    <div className="metric">
      <Icon size={18} />
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

function Alert({ tone, children }) {
  return <p className={`alert ${tone}`}>{children}</p>
}

function EmptyVisual({ icon: Icon }) {
  return (
    <div className="emptyVisual">
      <Icon size={36} />
    </div>
  )
}

function EmptyState({ icon: Icon, title, text }) {
  return (
    <div className="emptyState">
      <Icon size={34} />
      <strong>{title}</strong>
      <p>{text}</p>
    </div>
  )
}

function RaffleSkeleton() {
  return (
    <div className="rifaGrid">
      {[1, 2, 3].map((item) => (
        <div className="skeletonCard" key={item}>
          <span />
          <strong />
          <p />
          <p />
        </div>
      ))}
    </div>
  )
}

function DetailSkeleton() {
  return (
    <div className="detailSkeleton">
      <span />
      <strong />
      <p />
      <div />
    </div>
  )
}

function Progress({ value }) {
  const safeValue = Math.max(0, Math.min(Number(value) || 0, 100))
  return (
    <div className="progress" aria-label={`Progresso ${safeValue}%`}>
      <span style={{ width: `${safeValue}%` }} />
    </div>
  )
}

function Legend() {
  return (
    <div className="legend">
      <span className="available">Disponível</span>
      <span className="selectedLegend">Selecionado</span>
      <span className="reserved">Reservado</span>
      <span className="paid">Pago</span>
    </div>
  )
}

createRoot(document.getElementById('root')).render(<App />)
