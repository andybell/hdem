Pro batch_parabola_2points

envi, /restore_base_save_files
envi_batch_init, log_file='batch.log'

no_columns = 9            ; number of columns in csv file

startfile = 0             ; begin processing at this file number
;endfile   = 1            ; end   processing at this file number

max_pts = 20              ; the maximum number of points that will be calculated within a transect

; location of the input csv file indirectory  = 'E:\Users\ambell\Desktop\in\'
indirectory  = 'U:\HDEM_v4r4\channel_modifications\IDL\in\'
; location of the output csv file outdirectory = 'E:\Users\ambell\Desktop\out\'
outdirectory = 'U:\HDEM_v4r4\channel_modifications\IDL\out\'

wildcard = '*'
insuf  = '_in.txt'    ; input csv suffix
outsuf = '_trns'      ; output folder suffix
outcsv = '.txt'       ; output csv suffix

imagenamearray = file_search(indirectory  + wildcard + insuf)    ; read the names of csv files in the directory
numimages = n_elements(imagenamearray)                           ; number of csv files

; output filename array
outfldr = strarr(numimages)

; making array for .csv output files
filebasenamearray=strarr(numimages)
for i = 0, numimages-1 do begin
  filebasenamearray[i] = file_basename(imagenamearray[i])
  outfldr[i] = outdirectory + STRMID(filebasenamearray[i],0,STRPOS(filebasenamearray[i],insuf,/reverse_search)) + outsuf
endfor

endfile = numimages-1
if endfile lt startfile then endfile = numimages-1

; create the array that will contain co-ordinates
coord_3d = fltarr(3, 3)
    
for l = 0, numimages-1 do begin

    print, "Processing file: ", l, "   Name: ", filebasenamearray[l]
    
    ; read the template for .csv files
    readcol, imagenamearray[l], id, x1,y1,z1,x2,y2,z2, FORMAT = 'I,F,F,F,F,F,F', /PRESERVE_NULL, DELIMITER = ",", COUNT = tc, SKIPLINE=1, /SILENT
    
    ; create the directory for all transects in this csv file
    file_mkdir, outfldr[l]
    
    for i = 0, tc-1 do begin

      outfile = outfldr[l] + '\' + (file_basename(outfldr[l]) + '_' + strtrim(string(i+1), 1) + outcsv)
      
      coord_3d[0,0] = x1[i]
      coord_3d[0,1] = y1[i]
      coord_3d[0,2] = z1[i]
      coord_3d[1,0] = x2[i]
      coord_3d[1,1] = y2[i]
      coord_3d[1,2] = z2[i]
;      coord_3d[2,0] = x3[i]
;      coord_3d[2,1] = y3[i]
;      coord_3d[2,2] = z3[i]
      
      ; calculate depth all along the transect
      depth = calc_parabola(coord_3d)
      
      ; open csv file to write output
      openw, lun, outfile, /get_lun
      ; write the transect to a single csv file
      printf, lun, depth, FORMAT = '(3F12.2)'
      ; free the file pointer
      free_lun, lun
      
    endfor  ; end the number of rows (transects) in each csv file

endfor    ; end the number of CSV files (l)

  
;envi_batch_exit

return

End ;of Main Procedure

function calc_parabola, coord_3d

  ; array to contain 2-D co-ordinates
  coord_2d = fltarr(3, 2)
  
  x1 = coord_3d[0,0] 
  y1 = coord_3d[0,1] 
  z1 = coord_3d[0,2]
  x2 = coord_3d[1,0]
  y2 = coord_3d[1,1]
  z2 = coord_3d[1,2]
  
  if z1 lt z2 then begin
    x1 = coord_3d[1,0] 
    y1 = coord_3d[1,1] 
    z1 = coord_3d[1,2]
    x2 = coord_3d[0,0]
    y2 = coord_3d[0,1]
    z2 = coord_3d[0,2]
  endif
  
;  x3 = coord_3d[2,0]
;  y3 = coord_3d[2,1]
;  z3 = coord_3d[2,2]

  ; calculate x, y co-ordinates along the original transect line
  slope = float(y2 - y1)/float(x2 - x1)
  intercept = y1 - slope*x1
  
  dis = double(sqrt((x1 - x2)^2 + (y1 - y2)^2))

  ; distances between vertices
;  dis12 = double(sqrt((x1 - x2)^2 + (y1 - y2)^2))
;  dis23 = double(sqrt((x2 - x3)^2 + (y2 - y3)^2))
;  dis31 = double(sqrt((x3 - x1)^2 + (y3 - y1)^2))
  
;  dis3 = double((dis31^2 + dis23^2 - dis12^2)/(2*dis31))
;  dis1 = double(dis31 - dis3)
;  height = double(sqrt(dis23^2 - dis3^2))

  ; interval at which points should be calculated
  if dis le 50 then begin
    increment = 5
  endif else begin
    if dis le 100 then begin
      increment = 10
    endif else begin
      if dis le 500 then begin
        increment = 25
      endif else begin
        if dis le 1000 then begin
          increment = 50
        endif else begin
          increment =75
        endelse
      endelse
    endelse
  endelse

  ; array containing the 2d co-ordinates
  coord_2d = fltarr(3, 2)
  
  ; first point
  coord_2d[0, 0] = -1*dis/10   ; new x1
  coord_2d[0, 1] = z1          ; new y1

  ; second point
  coord_2d[1, 0] = 0           ; new x2
  coord_2d[1, 1] = z2          ; new y2

  ; third point
;  coord_2d[2, 0] = -1*dis3/10  ; new x3
;  coord_2d[2, 1] = z3          ; new y3

  ; vertex for both parabolas: (x2, y2)

  ; equation for first  parabola (between pts 1 and 2) - y = ax2 + b   w.r.t x-z plane co-ordinates
  ; y1 = a(x1 - x2) + y2, therefore
  ; a = (y1 - y2)/(x1 - x2)^2
  a1 = double((coord_2d[0, 1] - coord_2d[1, 1])/(coord_2d[0, 0] - coord_2d[1, 0])^2)
  b1 = double(coord_2d[0, 1] - a1*(coord_2d[0, 0]^2))

  ; equation for second parabola (between pts 2 and 3) - y = ax2 + b   w.r.t x-z plane co-ordinates
  ; y3 = a(x3 - x2) + y2, therefore
  ; a = (y3 - y2)/(x3 - x2)^2
;  a3 = double((coord_2d[2, 1] - coord_2d[1, 1])/(coord_2d[2, 0] - coord_2d[1, 0])^2)
;  b3 = double(coord_2d[2, 1] - a3*(coord_2d[2, 0]^2))

  ; array of depth calculated all along the transect at fixed lengths (increment)
  depth = dblarr(3, (fix(dis/increment) + 3))

  x_increment = double(abs(float(increment)/sqrt(slope^2 + 1)))
  y_increment = double(abs(slope*x_increment))
  if x1 gt x2 then x_increment = -1*x_increment
  if y1 gt y2 then y_increment = -1*y_increment

  increment = double(increment)/10
  
  count = 0
  ; calculating depth for transect
  for i = coord_2d[0, 0], 0, increment do begin
    depth[0, count] = x1 + x_increment*count
    depth[1, count] = y1 + y_increment*count
    depth[2, count] = double(a1*(i^2) + b1)
    count = count+1
  endfor
  
  depth[0, count] = x2
  depth[1, count] = y2
  depth[2, count] = z2

  return, depth
end
