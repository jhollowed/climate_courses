;********************************************************************************
; Created by Christiane Jablonowski 10/1/2010
;********************************************************************************
; Default: plots an X11 plot on the screen
; ncl steady_state_l2_error.ncl
; 
; Alternative: plot is stored as a png file, use command line setting, select l2 equation, Eq. (15) is default
; ncl 'pfmt="png"' eqn=14 steady_state_l2_error.ncl
; ncl 'pfmt="png"' eqn=15 steady_state_l2_error.ncl
;********************************************************************************

 load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
 load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
 load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
 
;********************************************************************************
; define function to an compute error norm
;********************************************************************************
 undef("l2_norma")  ; EQUATION 14 from Jablonowski and Williamson(2006), deviation from zonal symmetry
 function l2_norma( x[*][*][*][*]:numeric, wy[*], wz )
 local dimx, dimwz, rankwz, ntim, l2a, nt, xzon, xzonc \
     , dif2, wyc, wywz, wywzs
 begin
   dimx   = dimsizes( x )
   dimwz  = dimsizes( wz )
   rankwz = dimsizes( dimwz )
   
   ntim   = dimx(0)
   l2a    = new ( ntim, typeof(x), getFillValue(x) )
                                                       ; constant all times
   wyc    =  conform(x(0,:,:,:), wy, 1)                ; (klev,nlat,mlon)
 
   if (rankwz.eq.1) then                               ; constant weight
       wywz  = wyc*conform( x(0,:,:,:), wz, 0 )        ; (klev,nlat,mlon)
       wywzs = sum(wywz)                               ; scalar
       delete( wyc )
   end if
 
   do nt=0,ntim-1
      xzon    = dim_avg( x(nt,:,:,:) )                 ; (klev,nlat)
      xzonc   = conform( x(nt,:,:,:), xzon, (/0,1/))   ; (klev,nlat,mlon)
      dif2    = (x(nt,:,:,:)-xzonc)^2                  ; (klev,nlat,mlon)
      if (rankwz.eq.1) then
          l2a(nt) = sqrt( sum(dif2*wywz)/wywzs  )      ; (nt)
      else                                             ; variable wgt (nt)
          wywz    = wyc*wz(nt,:,:,:)                   ; (klev,nlat,mlon)
          l2a(nt) = sqrt( sum(dif2*wywz)/sum(wywz)  )  ; (nt)
      end if
   end do
 
   l2a@long_name = "l2: eqn 14" 
   if (isatt(x, "units")) then
      l2a@units = x@units
   end if
   
   return( l2a ) 
 end

;********************************************************************************
; define function to an compute error norm
;********************************************************************************
 undef("l2_normb")      ; EQUATION 15 from Jablonowski and Williamson (2006), comparison to initial state
 function l2_normb( x[*][*][*][*]:numeric, wy[*], wz )
 local dimx, dimwz, rankwz, ntim, l2b, nt, xzon0, xzonc \
     , dif2, wyc, wywz, wywz
 begin
   dimx    = dimsizes( x )
   dimwz   = dimsizes( wz )
   rankwz  = dimsizes( dimwz )
                                                      ; time=0
   xzon0   = dim_avg( x(0,:,:,:) )                    ; (klev,nlat)
   xzon0c  = conform( x(0,:,:,:), xzon0, (/0,1/))     ; (klev,nlat,mlon)    
   wyc     = conform( x(0,:,:,:), wy, 1)              ; (klev,nlat,mlon)
 
   if (rankwz.eq.1) then
       wywz  = wyc*conform( x(0,:,:,:), wz, 0 )       ; (klev,nlat,mlon)
       wywzs = sum(wywz)                              ; scalar
       delete( wyc )
   end if
   
   ntim = dimx(0)
   l2b  = new ( ntim, typeof(x), getFillValue(x) )
 
   do nt=0,ntim-1
      dif2    = (x(nt,:,:,:)-xzon0c)^2                ; (klev,nlat,mlon)
      if (rankwz.eq.1) then
          l2a(nt) = sqrt( sum(dif2*wywz)/wywzs  )     ; (nt)
      else
          wywz    = wyc*wz(nt,:,:,:)                  ; (klev,nlat,mlon)
          l2b(nt) = sqrt( sum(dif2*wywz)/sum(wywz) )  ; (nt)
      end if
   end do
 
   l2b@long_name = "l2" 
   if (isatt(x, "units")) then
      l2b@units = x@units
   end if
   return( l2b ) 
 end
 

;=======================================================================================
; Start of NCL script
; Calculate L2 NORMS
;======================================================================================= 
 begin

;=====
; declare the output directory and file
;=====
 files = dir+histf

;=====
; read command line settings: output format
;=====
  if (isvar("pfmt")) then            ; plot format specified on command line?
      type = pfmt                    ; read plot type from command line
  else
      if (.not.ismissing(getenv("PFMT"))) then   ; environment variable set?
          type = getenv("PFMT")   ; use environment variable .. if present
      else
          type = "X11"            ; default is "X11", other choices can be "eps", "pdf" or "png"
      end if
  end if

;=====
; read command line settings: l2 equation to compute
;=====
  if (isvar("eqn")) then            ; l2 equation specified on command line?
      l2_eqn = eqn                  ; read l2 equation number from command line
  else
      l2_eqn = 15                   ; default is Eq. (15) from Jablonowski and Williamson (2006) 
  end if

;=====
; declare the file name of the plot
;=====
 plotname = "steady_state_l2_error_Eq"+l2_eqn+"_"+dycore   ; file name

;=====
; open NetCDF file
;=====
   f0 = addfile (files , "r")

;--------------------------------------
;  read or set P0
;--------------------------------------
   if (isfilevar(f0, "P0")) then
       P0   = f0->P0                 ; Pa
   else
       P0 = 100000.
       P0@long_name = "reference pressure"
       P0@units     = "units"
   end if

;--------------------------------------
;  read or compute horizontal weights
;--------------------------------------
   if (isfilevar(f0, "gw")) then
       wy  = dble2flt( f0->gw )
   else
       rad = 4.*atan(1.)/180.
       lat = dble2flt( f0->lat )
       wy  = cos(lat*rad)      ; proxy [ sin(j+1/2)-sin(i-1/2) ]
   end if

;--------------------------------------
;  read hybrid coefficients
;--------------------------------------
   hyai = f0->hyai
   hybi = f0->hybi

;--------------------------------------
;  read surface pressure and zonal wind
;--------------------------------------
   ps0   = f0->PS
   u0    = f0->U

   printVarSummary( u0 )

;--------------------------------------
;  compute weights for hybrid vertical coordinate system
;--------------------------------------
   dp   = dpres_hybrid_ccm (ps0,P0,hyai,hybi)  ; Pa [kg/(m s2)]   
 
;--------------------------------------
;  compute the l2 norms
;--------------------------------------
   if (l2_eqn .eq. 14) then
     l2_0 = l2_norma( u0, wy, dp)   ; Eq. 14
   else
     l2_0 = l2_normb( u0, wy, dp)    ; Eq. 15
   end if
   printVarSummary( l2_0 )
   printMinMax( l2_0, True )

;************************************************
; plot
;************************************************
  
   data      = new((/1,dimsizes(l2_0)/),typeof(l2_0))
   data(0,:) = l2_0
   if (l2_eqn .eq. 14) then
     data@long_name = "l2 norm (Eq. 14)"
   else
     data@long_name = "l2 norm (Eq. 15)"
   end if
  
   wks   = gsn_open_wks (type,plotname) 
  
   res                   = True                      ; plot mods desired
   res@tiMainString      = "" 
   res@xyLineThicknesses = (/2.0/)                   ;
   res@xyLineColors      = (/"black"/)               ; change line color
   res@xyMonoDashPattern = False                     ; each solid
   res@xyMonoLineThickness=True                      ; all same thick
   res@xyLineThicknessF   = 2
   res@vpWidthF        = 0.5
   res@vpHeightF       = 0.32
   res@tiXAxisString   = "Day"
   res@tiYAxisString   = ""
                           
   res@gsnFrame = False

   res@pmLegendDisplayMode    = "Always"              ; turn on legend
   res@pmLegendSide           = "Top"                 ; Change location of 
   res@pmLegendParallelPosF   = .19                   ; move units right
   res@pmLegendOrthogonalPosF = -0.44                 ; more neg = down
   res@pmLegendWidthF         = 0.10                  ; Change width and
   res@pmLegendHeightF        = 0.15                  ; height of legend.
   res@lgLabelFontHeightF     = .015                  ; change font height
;   res@lgPerimOn              = True
   res@lgPerimOn              = False
   res@xyExplicitLegendLabels = (/dycore/)
;   res@xyExplicitLegendLabels = (/" ~F8~e~F21~ = 0"," ~F8~e~F21~ = 0.1"," ~F8~e~F21~ = 0.2"," ~F8~e~F21~ = 0.3"/)
  
   plot  = gsn_csm_y (wks,data,res) ; create plot

; text for axis label
   txres                                   = True
   txres@txAngleF                          = 90.
   txres@txFuncCode    = ":" 
   txres@txFontHeightF                     = .018
   if (l2_eqn .eq. 14) then
     gsn_text_ndc(wks,"l:B:2:N: norm (Eq. 14)",.115,.64,txres)
   else
     gsn_text_ndc(wks,"l:B:2:N: norm (Eq. 15)",.115,.64,txres)
   end if

   frame(wks)                                     ; now advance

;  trim the white space
  if (type .ne. "X11") then
    system("convert -trim "+plotname+"."+pfmt+" "+plotname+"."+pfmt)
  end if

 end
